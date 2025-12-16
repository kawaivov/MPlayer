/* static/js/script.js */

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchInput');

    // 1. Ініціалізація плеєрів (проходимось по всіх кнопках Play, що вже є в HTML)
    const playButtons = document.querySelectorAll('.play-btn');
    
    playButtons.forEach(btn => {
        const id = btn.getAttribute('data-id');
        // Перевіряємо, чи пісня не "disabled" (батьківський елемент)
        const songContainer = document.getElementById(`song-${id}`);
        
        if (!songContainer.classList.contains('disabled')) {
            setupPlayer(id);
        }
    });

    // 2. Логіка ПОШУКУ (фільтрація вже існуючих елементів)
    searchInput.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        const allSongDivs = document.querySelectorAll('.song-item');

        allSongDivs.forEach(div => {
            // Ми зберегли назву і артиста в data-атрибутах в HTML (дивись крок 2)
            const title = div.getAttribute('data-title');
            const artist = div.getAttribute('data-artist');

            if (title.includes(searchTerm) || artist.includes(searchTerm)) {
                div.style.display = 'flex'; // Показати
            } else {
                div.style.display = 'none'; // Сховати
            }
        });
    });

    // 3. Логіка одного плеєра
    function setupPlayer(id) {
        const audio = document.getElementById(`audio-${id}`);
        const playBtn = document.getElementById(`play-btn-${id}`);
        const slider = document.getElementById(`seek-${id}`);

        playBtn.addEventListener('click', () => {
            if (audio.paused) {
                // Пауза для всіх інших
                document.querySelectorAll('audio').forEach(el => {
                    if (el !== audio) {
                        el.pause();
                        const otherId = el.id.split('-')[1];
                        const otherBtn = document.getElementById(`play-btn-${otherId}`);
                        if(otherBtn) otherBtn.innerText = '▶';
                    }
                });
                audio.play();
                playBtn.innerText = '⏸';
            } else {
                audio.pause();
                playBtn.innerText = '▶';
            }
        });

        audio.addEventListener('timeupdate', () => {
            if (!audio.duration) return;
            const progress = (audio.currentTime / audio.duration) * 100;
            slider.value = progress;
            slider.style.background = `linear-gradient(to right, #1db954 ${progress}%, #535353 ${progress}%)`;
        });

        slider.addEventListener('input', () => {
            const time = (slider.value / 100) * audio.duration;
            audio.currentTime = time;
        });

        audio.addEventListener('ended', () => {
            playBtn.innerText = '▶';
            slider.value = 0;
            slider.style.background = '#535353';
        });
    }
});

// Глобальна функція видалення
window.deleteSong = function(id) {
    if (!confirm('Видалити?')) return;
    fetch(`/delete/${id}`, { method: 'POST' })
        .then(r => r.json())
        .then(data => {
            if(data.success) {
                 const el = document.getElementById(`song-${id}`);
                 el.style.opacity = '0';
                 setTimeout(() => el.remove(), 300);
            } else {
                alert("Помилка: " + data.message);
            }
        });
};