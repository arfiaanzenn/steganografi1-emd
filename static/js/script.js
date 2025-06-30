// static/js/script.js

document.addEventListener('DOMContentLoaded', function() {
    // Fungsi untuk mengelola tab
    window.openTab = function(evt, tabName) {
        var i, tabcontent, tablinks;
        tabcontent = document.getElementsByClassName("tab-content");
        for (i = 0; i < tabcontent.length; i++) {
            tabcontent[i].style.display = "none";
            tabcontent[i].classList.remove('active');
        }
        tablinks = document.getElementsByClassName("tab-button");
        for (i = 0; i < tablinks.length; i++) {
            tablinks[i].classList.remove("active");
        }
        document.getElementById(tabName).style.display = "block";
        document.getElementById(tabName).classList.add('active');
        evt.currentTarget.classList.add("active");
    };

    // Tampilkan tab pertama secara default
    document.getElementsByClassName("tab-content")[0].style.display = "block";

    // --- Pengiriman Form Sisipkan Pesan ---
    const embedForm = document.getElementById('embed-form');
    if (embedForm) {
        embedForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(embedForm);
            const resultBox = document.getElementById('embed-result');
            resultBox.innerHTML = '<h3>Memproses...</h3>';

            try {
                const response = await fetch('/steganography', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (response.ok) {
                    // Tampilkan hasil
                    resultBox.innerHTML = `
                        <h3>${data.message}</h3>
                        <img src="${data.image}" alt="Stego Image">
                        <a href="${data.image}" download="stego_image.png" class="download-link">Unduh Gambar Stego</a>
                    `;
                } else {
                    // Tampilkan error
                    resultBox.innerHTML = `<h3 style="color: red;">Error: ${data.error}</h3>`;
                }
            } catch (error) {
                resultBox.innerHTML = `<h3 style="color: red;">Terjadi kesalahan: ${error.message}</h3>`;
            }
        });
    }

    // --- Pengiriman Form Ekstrak Pesan ---
    const extractForm = document.getElementById('extract-form');
    if (extractForm) {
        extractForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(extractForm);
            const resultBox = document.getElementById('extract-result');
            resultBox.innerHTML = '<h3>Memproses...</h3>';

            try {
                const response = await fetch('/steganography', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (response.ok) {
                    // Tampilkan hasil
                    resultBox.innerHTML = `
                        <h3>${data.message}</h3>
                        <p><strong>Pesan yang Diekstrak:</strong></p>
                        <p>${data.extracted_message}</p>
                    `;
                } else {
                    // Tampilkan error
                    resultBox.innerHTML = `<h3 style="color: red;">Error: ${data.error}</h3>`;
                }
            } catch (error) {
                resultBox.innerHTML = `<h3 style="color: red;">Terjadi kesalahan: ${error.message}</h3>`;
            }
        });
    }
});