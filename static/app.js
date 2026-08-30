let currentMethod = 'classic';
let copyTimerInterval = null;
let analyzeDebounceTimer = null;
let generateDebounceTimer = null;

document.addEventListener('DOMContentLoaded', () => {
    initializeGenerator();
    initializeAnalyzer();
    generatePassword();
});

function initializeGenerator() {
    const methodSelect = document.getElementById('method-select');
    const refreshBtn = document.getElementById('refresh-btn');
    const copyBtn = document.getElementById('copy-btn');

    methodSelect.addEventListener('change', (e) => {
        currentMethod = e.target.value;
        updateOptionsVisibility();
        generatePassword();
    });

    refreshBtn.addEventListener('click', generatePassword);

    copyBtn.addEventListener('click', copyPassword);

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
        params.length = parseInt(document.getElementById('length-slider').value);
        params.use_upper = document.getElementById('use-upper').checked;
        params.use_lower = document.getElementById('use-lower').checked;
        params.use_digits = document.getElementById('use-digits').checked;
        params.use_symbols = document.getElementById('use-symbols').checked;
        params.exclude_chars = document.getElementById('exclude-chars').value;
        params.min_of_each = document.getElementById('min-of-each').checked;
    } else if (currentMethod === 'passphrase') {
        params.word_count = parseInt(document.getElementById('word-count-slider').value);
        params.separator = document.getElementById('separator').value;
        params.capitalize = document.getElementById('capitalize').checked;
        params.add_number = document.getElementById('add-number').checked;
        params.add_symbol = document.getElementById('add-symbol').checked;
    } else if (currentMethod === 'pronounceable') {
        params.length = parseInt(document.getElementById('pronounceable-length-slider').value);
    } else if (currentMethod === 'pattern') {
        params.pattern_template = document.getElementById('pattern-template').value;
    }

    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        if (data.status === 'success') {
            document.getElementById('generated-password').textContent = data.password;
        } else {
            showError('Ошибка генерации: ' + (data.error || 'неизвестная ошибка'));
        }
    } catch (error) {
        showError('Ошибка соединения с сервером');
        console.error('Generate error:', error);
    }
}

async function copyPassword() {
    const password = document.getElementById('generated-password').textContent;
    if (!password) return;

    try {
        await navigator.clipboard.writeText(password);

        const copyBtn = document.getElementById('copy-btn');
        const originalText = copyBtn.innerHTML;
        copyBtn.innerHTML = '✓ Скопировано!';
        copyBtn.style.background = 'var(--success)';

        setTimeout(() => {
            copyBtn.innerHTML = originalText;
            copyBtn.style.background = '';
        }, 2000);

        startCopyTimer();
    } catch (error) {
        showError('Не удалось скопировать в буфер обмена');
        console.error('Copy error:', error);
    }
}

function startCopyTimer() {
    const timerElement = document.getElementById('copy-timer');
    const secondsElement = document.getElementById('timer-seconds');

    let seconds = 30;
    timerElement.style.display = 'block';
    secondsElement.textContent = seconds;

    if (copyTimerInterval) {
        clearInterval(copyTimerInterval);
    }

    copyTimerInterval = setInterval(() => {
        seconds--;
        secondsElement.textContent = seconds;

        if (seconds <= 0) {
            clearInterval(copyTimerInterval);
            timerElement.style.display = 'none';

            navigator.clipboard.writeText('').catch(() => {
                console.log('Не удалось очистить буфер обмена');
            });
        }
    }, 1000);
}

function initializeAnalyzer() {
    const analyzeInput = document.getElementById('analyze-input');
    const toggleBtn = document.getElementById('toggle-visibility');

    analyzeInput.addEventListener('input', debounceAnalyze);

    toggleBtn.addEventListener('click', () => {
        const input = document.getElementById('analyze-input');
        if (input.type === 'password') {
            input.type = 'text';
            toggleBtn.textContent = '🙈';
        } else {
            input.type = 'password';
            toggleBtn.textContent = '👁';
        }
    });
}

function debounceAnalyze() {
    clearTimeout(analyzeDebounceTimer);
    analyzeDebounceTimer = setTimeout(analyzePassword, 300);
}

async function analyzePassword() {
    const password = document.getElementById('analyze-input').value;
    const resultsElement = document.getElementById('analysis-results');

    if (!password) {
        resultsElement.style.display = 'none';
        return;
    }

    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ password })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        if (data.status === 'success') {
            displayAnalysisResults(data.analysis);
            resultsElement.style.display = 'block';
        } else {
            showError('Ошибка анализа: ' + (data.error || 'неизвестная ошибка'));
        }
    } catch (error) {
        showError('Ошибка соединения с сервером');
        console.error('Analyze error:', error);
    }
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

    strengthBar.style.width = `${scoreToPercent[analysis.score]}%`;
    strengthBar.style.backgroundColor = scoreToColor[analysis.score];
    strengthLabel.textContent = scoreToText[analysis.score];
    strengthLabel.style.color = scoreToColor[analysis.score];

    document.getElementById('entropy-value').textContent = Math.round(analysis.entropy_bits);

    const warningsElement = document.getElementById('warnings');
    warningsElement.innerHTML = '';
    if (analysis.warnings && analysis.warnings.length > 0) {
        analysis.warnings.forEach(warning => {
            const item = document.createElement('div');
            item.className = 'feedback-item warning';
            item.innerHTML = `
                <span class="feedback-icon">⚠️</span>
                <span class="feedback-text">${warning}</span>
            `;
            warningsElement.appendChild(item);
        });
    }

    const suggestionsElement = document.getElementById('suggestions');
    suggestionsElement.innerHTML = '';
    if (analysis.suggestions && analysis.suggestions.length > 0) {
        analysis.suggestions.forEach(suggestion => {
            const item = document.createElement('div');
            item.className = 'feedback-item suggestion';
            item.innerHTML = `
                <span class="feedback-icon">💡</span>
                <span class="feedback-text">${suggestion}</span>
            `;
            suggestionsElement.appendChild(item);
        });
    }

    const detailsElement = document.getElementById('technical-details');
    detailsElement.innerHTML = '';
    const details = analysis.details;

    const detailRows = [
        ['Длина', details.length],
        ['Размер алфавита', details.charset_size],
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
        row.innerHTML = `
            <span class="detail-label">${label}</span>
            <span class="detail-value">${value}</span>
        `;
        detailsElement.appendChild(row);
    });

    if (analysis.crack_times) {
        displayCrackTimes(analysis.crack_times);
    }
}

function displayCrackTimes(crackTimes) {
    const container = document.getElementById('crack-times');
    container.innerHTML = '';

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

        card.innerHTML = `
            <div class="crack-time-header">
                <span class="crack-time-icon">${icons[key] || '🔓'}</span>
                <span class="crack-time-name">${data.name}</span>
            </div>
            <div class="crack-time-description">${data.description}</div>
            <div class="crack-time-value ${colorClass}">${data.display}</div>
        `;

        container.appendChild(card);
    });
}

function showError(message) {
    console.error(message);
}