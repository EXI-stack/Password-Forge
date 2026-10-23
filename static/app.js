let currentMethod = 'classic';
let copyTimerInterval = null;
let analyzeDebounceTimer = null;
let generateDebounceTimer = null;
let lastCopiedPassword = null;
let lastGeneratedAnalysis = null;
let pendingClipboardClearHandler = null;

document.addEventListener('DOMContentLoaded', () => {
    initializeGenerator();
    initializeAnalyzer();
    generatePassword();
});

function initializeGenerator() {
    const methodSelect = document.getElementById('method-select');
    const refreshBtn = document.getElementById('refresh-btn');
    const copyBtn = document.getElementById('copy-btn');
    const analyzeGenBtn = document.getElementById('analyze-generated-btn');

    methodSelect.addEventListener('change', (e) => {
        currentMethod = e.target.value;
        hideError();
        updateOptionsVisibility();
        generatePassword();
    });

    refreshBtn.addEventListener('click', generatePassword);
    copyBtn.addEventListener('click', copyPassword);

    if (analyzeGenBtn) {
        analyzeGenBtn.addEventListener('click', () => {
            const pwd = document.getElementById('generated-password').textContent;
            if (!pwd) return;
            const input = document.getElementById('analyze-input');
            input.value = pwd;
            analyzePassword();
            input.scrollIntoView({ behavior: 'smooth', block: 'center' });
        });
    }

    initializeClassicOptions();
    initializePassphraseOptions();
    initializePronounceableOptions();
    initializePatternOptions();
}

function initializeClassicOptions() {
    const lengthSlider = document.getElementById('length-slider');
    const lengthValue = document.getElementById('length-value');

    lengthSlider.addEventListener('input', (e) => {
        lengthValue.textContent = e.target.value;
        debounceGenerate();
    });

    const checkboxes = ['use-upper', 'use-lower', 'use-digits', 'use-symbols', 'min-of-each'];
    checkboxes.forEach(id => {
        document.getElementById(id).addEventListener('change', debounceGenerate);
    });

    document.getElementById('exclude-chars').addEventListener('input', debounceGenerate);
}

function initializePassphraseOptions() {
    const wordCountSlider = document.getElementById('word-count-slider');
    const wordCountValue = document.getElementById('word-count-value');

    wordCountSlider.addEventListener('input', (e) => {
        wordCountValue.textContent = e.target.value;
        debounceGenerate();
    });

    document.getElementById('separator').addEventListener('input', debounceGenerate);

    const checkboxes = ['capitalize', 'add-number', 'add-symbol'];
    checkboxes.forEach(id => {
        document.getElementById(id).addEventListener('change', debounceGenerate);
    });
}

function initializePronounceableOptions() {
    const lengthSlider = document.getElementById('pronounceable-length-slider');
    const lengthValue = document.getElementById('pronounceable-length-value');

    lengthSlider.addEventListener('input', (e) => {
        lengthValue.textContent = e.target.value;
        debounceGenerate();
    });
}

function initializePatternOptions() {
    document.getElementById('pattern-template').addEventListener('input', debounceGenerate);
}

function updateOptionsVisibility() {
    const options = ['classic', 'passphrase', 'pronounceable', 'pattern'];
    options.forEach(method => {
        const element = document.getElementById(`${method}-options`);
        if (element) {
            element.style.display = method === currentMethod ? 'block' : 'none';
        }
    });
}

function debounceGenerate() {
    clearTimeout(generateDebounceTimer);
    generateDebounceTimer = setTimeout(generatePassword, 150);
}

async function generatePassword() {
    const params = { method: currentMethod };

    if (currentMethod === 'classic') {
        params.length = parseInt(document.getElementById('length-slider').value, 10);
        params.use_upper = document.getElementById('use-upper').checked;
        params.use_lower = document.getElementById('use-lower').checked;
        params.use_digits = document.getElementById('use-digits').checked;
        params.use_symbols = document.getElementById('use-symbols').checked;
        params.exclude_chars = document.getElementById('exclude-chars').value;
        params.min_of_each = document.getElementById('min-of-each').checked;
    } else if (currentMethod === 'passphrase') {
        params.word_count = parseInt(document.getElementById('word-count-slider').value, 10);
        params.separator = document.getElementById('separator').value;
        params.capitalize = document.getElementById('capitalize').checked;
        params.add_number = document.getElementById('add-number').checked;
        params.add_symbol = document.getElementById('add-symbol').checked;
    } else if (currentMethod === 'pronounceable') {
        params.length = parseInt(document.getElementById('pronounceable-length-slider').value, 10);
    } else if (currentMethod === 'pattern') {
        params.pattern_template = document.getElementById('pattern-template').value;
    }

    try {
        const response = await fetch('/api/full', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        });

        const data = await response.json().catch(() => ({}));

        if (!response.ok || data.status !== 'success') {
            showError(data.error || `Ошибка генерации (HTTP ${response.status})`);
            return;
        }

        hideError();
        document.getElementById('generated-password').textContent = data.password;
        lastGeneratedAnalysis = data.analysis;

        const analyzeInput = document.getElementById('analyze-input');
        if (!analyzeInput.value && data.analysis && data.analysis.crack_times) {
            displayCrackTimes(data.analysis.crack_times, '(сгенерированный пароль)');
        }
    } catch (error) {
        showError('Ошибка соединения с локальным сервером');
        console.error('Generate error:', error);
    }
}

async function writeToClipboard(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(text);
        return;
    }
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.focus();
    textarea.select();
    const ok = document.execCommand('copy');
    document.body.removeChild(textarea);
    if (!ok) {
        throw new Error('execCommand copy failed');
    }
}

async function copyPassword() {
    const password = document.getElementById('generated-password').textContent;
    if (!password) return;

    try {
        await writeToClipboard(password);
        lastCopiedPassword = password;

        const copyBtn = document.getElementById('copy-btn');
        const originalText = '📋 Копировать';
        copyBtn.textContent = '✓ Скопировано!';
        copyBtn.style.background = 'var(--success)';

        setTimeout(() => {
            copyBtn.textContent = originalText;
            copyBtn.style.background = '';
        }, 2000);

        startCopyTimer(password);
    } catch (error) {
        showError('Не удалось скопировать пароль в буфер обмена');
        console.error('Copy error:', error);
    }
}

async function safelyClearClipboard(expectedPassword) {
    const timerElement = document.getElementById('copy-timer');

    if (pendingClipboardClearHandler) {
        window.removeEventListener('focus', pendingClipboardClearHandler);
        pendingClipboardClearHandler = null;
    }

    try {
        if (navigator.clipboard && navigator.clipboard.readText) {
            try {
                const currentClip = await navigator.clipboard.readText();
                if (currentClip && currentClip !== expectedPassword) {
                    timerElement.style.display = 'none';
                    lastCopiedPassword = null;
                    return;
                }
            } catch (_) {
            }
        }

        if (lastCopiedPassword === expectedPassword) {
            await writeToClipboard('');
            lastCopiedPassword = null;
        }
        timerElement.style.display = 'none';
    } catch (err) {
        timerElement.textContent = 'Буфер будет очищен при возврате в окно...';
        pendingClipboardClearHandler = () => {
            safelyClearClipboard(expectedPassword);
        };
        window.addEventListener('focus', pendingClipboardClearHandler, { once: true });
    }
}

function startCopyTimer(copiedPassword) {
    const timerElement = document.getElementById('copy-timer');

    if (copyTimerInterval) {
        clearInterval(copyTimerInterval);
    }
    if (pendingClipboardClearHandler) {
        window.removeEventListener('focus', pendingClipboardClearHandler);
        pendingClipboardClearHandler = null;
    }

    let seconds = 30;
    timerElement.style.display = 'block';
    timerElement.innerHTML = 'Буфер очистится через <span id="timer-seconds">30</span> сек...';
    const secondsElement = document.getElementById('timer-seconds');

    copyTimerInterval = setInterval(() => {
        seconds--;
        if (secondsElement) {
            secondsElement.textContent = seconds;
        }

        if (seconds <= 0) {
            clearInterval(copyTimerInterval);
            copyTimerInterval = null;
            safelyClearClipboard(copiedPassword);
        }
    }, 1000);
}

function initializeAnalyzer() {
    const analyzeInput = document.getElementById('analyze-input');
    const toggleBtn = document.getElementById('toggle-visibility');

    analyzeInput.addEventListener('input', debounceAnalyze);

    toggleBtn.addEventListener('click', () => {
        if (analyzeInput.type === 'password') {
            analyzeInput.type = 'text';
            toggleBtn.textContent = '🙈';
        } else {
            analyzeInput.type = 'password';
            toggleBtn.textContent = '👁';
        }
    });
}

function debounceAnalyze() {
    clearTimeout(analyzeDebounceTimer);
    analyzeDebounceTimer = setTimeout(analyzePassword, 250);
}

async function analyzePassword() {
    const password = document.getElementById('analyze-input').value;
    const resultsElement = document.getElementById('analysis-results');

    if (!password) {
        resultsElement.style.display = 'none';
        if (lastGeneratedAnalysis && lastGeneratedAnalysis.crack_times) {
            displayCrackTimes(lastGeneratedAnalysis.crack_times, '(сгенерированный пароль)');
        } else {
            document.getElementById('crack-times').innerHTML = '';
            document.getElementById('crack-target-label').textContent = '';
        }
        return;
    }

    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ password })
        });

        const data = await response.json().catch(() => ({}));

        if (!response.ok || data.status !== 'success') {
            showError(data.error || `Ошибка анализа (HTTP ${response.status})`);
            return;
        }

        displayAnalysisResults(data.analysis);
        resultsElement.style.display = 'block';
    } catch (error) {
        showError('Ошибка соединения с сервером при анализе');
        console.error('Analyze error:', error);
    }
}

function createFeedbackItem(type, icon, text) {
    const item = document.createElement('div');
    item.className = `feedback-item ${type}`;

    const iconSpan = document.createElement('span');
    iconSpan.className = 'feedback-icon';
    iconSpan.textContent = icon;

    const textSpan = document.createElement('span');
    textSpan.className = 'feedback-text';
    textSpan.textContent = text;

    item.appendChild(iconSpan);
    item.appendChild(textSpan);
    return item;
}

function displayAnalysisResults(analysis) {
    const strengthBar = document.getElementById('strength-bar');
    const strengthLabel = document.getElementById('strength-label');

    const scoreToPercent = { 0: 10, 1: 30, 2: 50, 3: 75, 4: 100 };
    const scoreToColor = {
        0: '#ef4444',
        1: '#f97316',
        2: '#fbbf24',
        3: '#84cc16',
        4: '#22c55e'
    };
    const scoreToText = {
        0: 'Ужасный',
        1: 'Слабый',
        2: 'Средний',
        3: 'Хороший',
        4: 'Отличный'
    };

    strengthBar.style.width = `${scoreToPercent[analysis.score] ?? 10}%`;
    strengthBar.style.backgroundColor = scoreToColor[analysis.score] || '#ef4444';
    strengthLabel.textContent = scoreToText[analysis.score] || 'Ужасный';
    strengthLabel.style.color = scoreToColor[analysis.score] || '#ef4444';

    const effectiveEntropy = analysis.effective_entropy !== undefined
        ? analysis.effective_entropy
        : analysis.entropy_bits;
    document.getElementById('entropy-value').textContent = Math.round(effectiveEntropy);

    const warningsElement = document.getElementById('warnings');
    warningsElement.innerHTML = '';
    if (Array.isArray(analysis.warnings)) {
        analysis.warnings.forEach(warning => {
            warningsElement.appendChild(createFeedbackItem('warning', '⚠️', warning));
        });
    }

    const suggestionsElement = document.getElementById('suggestions');
    suggestionsElement.innerHTML = '';
    if (Array.isArray(analysis.suggestions)) {
        analysis.suggestions.forEach(suggestion => {
            suggestionsElement.appendChild(createFeedbackItem('suggestion', '💡', suggestion));
        });
    }

    const detailsElement = document.getElementById('technical-details');
    detailsElement.innerHTML = '';
    const details = analysis.details;

    const detailRows = [
        ['Длина', details.length],
        ['Размер алфавита', details.charset_size],
        ['Эффективная энтропия', `${effectiveEntropy.toFixed(1)} бит`],
        ['Математическая энтропия', `${analysis.entropy_bits.toFixed(1)} бит`],
        ['Заглавные буквы', details.has_upper ? '✓' : '✗'],
        ['Строчные буквы', details.has_lower ? '✓' : '✗'],
        ['Цифры', details.has_digit ? '✓' : '✗'],
        ['Спецсимволы', details.has_symbol ? '✓' : '✗'],
        ['Штраф за повторы', details.repeat_penalty.toFixed(2)],
        ['Штраф за последовательности', details.sequence_penalty.toFixed(2)],
        ['Штраф за клавиатурные паттерны', details.keyboard_penalty.toFixed(2)],
        ['Штраф за словарные слова', details.dictionary_penalty.toFixed(2)],
        ['Частый пароль', details.is_common ? 'Да' : 'Нет']
    ];

    detailRows.forEach(([label, value]) => {
        const row = document.createElement('div');
        row.className = 'detail-row';

        const labelSpan = document.createElement('span');
        labelSpan.className = 'detail-label';
        labelSpan.textContent = label;

        const valueSpan = document.createElement('span');
        valueSpan.className = 'detail-value';
        valueSpan.textContent = String(value);

        row.appendChild(labelSpan);
        row.appendChild(valueSpan);
        detailsElement.appendChild(row);
    });

    if (analysis.crack_times) {
        displayCrackTimes(analysis.crack_times, '(проверяемый пароль)');
    }
}

function displayCrackTimes(crackTimes, sourceLabelText = '') {
    const container = document.getElementById('crack-times');
    const targetLabel = document.getElementById('crack-target-label');
    container.innerHTML = '';

    if (targetLabel) {
        targetLabel.textContent = sourceLabelText;
    }

    const icons = {
        online_throttled: '🌐',
        online_no_throttle: '⚡',
        offline_slow_hash: '🔒',
        offline_fast_hash: '💻'
    };

    Object.entries(crackTimes).forEach(([key, data]) => {
        const card = document.createElement('div');
        card.className = 'crack-time-card';

        let colorClass = 'safe';
        if (data.seconds < 3600) {
            colorClass = 'danger';
        } else if (data.seconds < 31536000) {
            colorClass = 'warning';
        } else if (data.seconds < 31536000 * 1000) {
            colorClass = 'caution';
        }

        const header = document.createElement('div');
        header.className = 'crack-time-header';

        const iconSpan = document.createElement('span');
        iconSpan.className = 'crack-time-icon';
        iconSpan.textContent = icons[key] || '🔓';

        const nameSpan = document.createElement('span');
        nameSpan.className = 'crack-time-name';
        nameSpan.textContent = data.name;

        header.appendChild(iconSpan);
        header.appendChild(nameSpan);

        const descDiv = document.createElement('div');
        descDiv.className = 'crack-time-description';
        descDiv.textContent = data.description;

        const valDiv = document.createElement('div');
        valDiv.className = `crack-time-value ${colorClass}`;
        valDiv.textContent = data.display;

        card.appendChild(header);
        card.appendChild(descDiv);
        card.appendChild(valDiv);

        container.appendChild(card);
    });
}

function showError(message) {
    const banner = document.getElementById('error-banner');
    const text = document.getElementById('error-text');
    if (banner && text) {
        text.textContent = message;
        banner.style.display = 'flex';
    }
    console.error(message);
}

function hideError() {
    const banner = document.getElementById('error-banner');
    if (banner) {
        banner.style.display = 'none';
    }
}
