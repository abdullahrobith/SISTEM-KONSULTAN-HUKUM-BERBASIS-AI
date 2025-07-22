document.addEventListener('DOMContentLoaded', function() {
    const showQuestionBoxBtn = document.getElementById('show-question-box');
    const questionBoxContainer = document.getElementById('question-box-container');
    const form = questionBoxContainer.querySelector('form');
    const questionInput = document.getElementById('question-input');
    
    const micButtonFixed = document.getElementById('mic-button-fixed');
    const micButtonForm = document.getElementById('mic-button');
    
    const submitButton = form.querySelector('button[type="submit"]');
    const stopButton = document.getElementById('stop-button');
    
    // --- Elemen baru untuk overlay ---
    const loadingOverlay = document.getElementById('loading-overlay'); 
    const loadingDiv = document.getElementById('loading'); // Spinner itu sendiri
    const haruThinkingDiv = document.getElementById('haru-thinking'); // Teks thinking

    const haruBubble = document.getElementById('haru-bubble');
    
    let recognition;
    let speechUtterance = null;
    let lipSyncInterval = null;

    // Fungsi untuk menampilkan bubble chat Haru
    function showHaruBubble(message) {
        haruBubble.innerHTML = message;
        haruBubble.style.display = 'block';
        haruBubble.classList.add('fade-in');
    }

    // Fungsi untuk menyembunyikan bubble chat Haru
    function hideHaruBubble() {
        haruBubble.classList.remove('fade-in');
        haruBubble.classList.add('fade-out');
        setTimeout(() => {
            haruBubble.style.display = 'none';
            haruBubble.classList.remove('fade-out');
        }, 300);
    }

    // Fungsi untuk menampilkan overlay loading
    function showLoadingOverlay() {
        loadingOverlay.classList.add('show'); // Aktifkan transisi opacity
        loadingDiv.style.display = 'block'; // Tampilkan spinner
        haruThinkingDiv.style.display = 'block'; // Tampilkan teks thinking
    }

    // Fungsi untuk menyembunyikan overlay loading
    function hideLoadingOverlay() {
        loadingOverlay.classList.remove('show'); // Nonaktifkan transisi opacity
        // Setelah transisi selesai, sembunyikan elemen display-nya
        setTimeout(() => {
            loadingDiv.style.display = 'none';
            haruThinkingDiv.style.display = 'none';
        }, 300); // Sesuaikan dengan durasi transisi CSS
    }


    // Awalnya sembunyikan question box
    questionBoxContainer.style.display = 'none';
    showQuestionBoxBtn.style.display = 'block';

    if (showQuestionBoxBtn) {
        showQuestionBoxBtn.addEventListener('click', function() {
            questionBoxContainer.style.display = 'block';
            showQuestionBoxBtn.style.display = 'none';
            if (micButtonFixed) {
                micButtonFixed.style.display = 'none'; 
            }
            questionBoxContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
        });
    }

    function handleMicButtonClick() {
        if (!('webkitSpeechRecognition' in window)) {
            alert('Maaf, browser Anda tidak mendukung Speech Recognition.');
            return;
        }

        recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'id-ID';

        if (window.live2dModel) {
            window.live2dModel.motion("", 7);
        }

        recognition.onstart = function() {
            if (micButtonFixed) micButtonFixed.disabled = true;
            if (micButtonForm) micButtonForm.disabled = true;
            if (micButtonForm) micButtonForm.textContent = 'Mendengarkan...'; 
            submitButton.disabled = true;
            stopButton.style.display = 'inline-block';
            showHaruBubble("Aku mendengarkanmu. Silakan ajukan pertanyaan hukummu.");
        };

        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            questionInput.value = transcript;

            if (questionBoxContainer.style.display === 'none') {
                 questionBoxContainer.style.display = 'block';
                 showQuestionBoxBtn.style.display = 'none';
                 if (micButtonFixed) micButtonFixed.style.display = 'none';
                 questionBoxContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
            // ✅ Submit otomatis setelah input suara selesai
            // Tidak perlu delay, biarkan browser langsung submit
            form.requestSubmit(); 
        };

        recognition.onerror = function(event) {
            console.error('Speech recognition error:', event.error);
            if (micButtonFixed) micButtonFixed.disabled = false;
            if (micButtonForm) micButtonForm.disabled = false;
            if (micButtonForm) micButtonForm.textContent = '🎤 Tanya Lewat Suara';
            submitButton.disabled = false;
            stopButton.style.display = 'none';
            showHaruBubble("Maaf, ada kesalahan dalam pengenalan suara. Coba lagi.");
            setTimeout(hideHaruBubble, 3000);
        };

        recognition.onend = function() {
            // micButtonFixed dan micButtonForm akan direset oleh pageshow atau setelah form submit
            // Tidak perlu reset di sini, kecuali jika tidak ada transcript yang didapatkan
            if (questionInput.value.trim() === "") { // Jika tidak ada suara yang terdeteksi
                if (micButtonFixed) micButtonFixed.disabled = false;
                if (micButtonForm) micButtonForm.disabled = false;
                if (micButtonForm) micButtonForm.textContent = '🎤 Tanya Lewat Suara';
                submitButton.disabled = false;
                stopButton.style.display = 'none';
                hideHaruBubble();
            }
        };

        recognition.start();
    }

    if (micButtonFixed) {
        micButtonFixed.addEventListener('click', handleMicButtonClick);
    }
    if (micButtonForm) {
        micButtonForm.addEventListener('click', handleMicButtonClick);
    }

    if (stopButton) {
        stopButton.addEventListener('click', function() {
            if (recognition) {
                recognition.stop(); 
            }
            window.speechSynthesis.cancel(); 
            stopButton.style.display = "none";
            // Sembunyikan bubble dan reset Live2D secara langsung
            hideHaruBubble();
            clearInterval(lipSyncInterval);
            if (window.live2dModel) {
                const model = window.live2dModel.internalModel.coreModel;
                model.setParameterValueById("ParamMouthOpenY", 0);
                window.live2dModel.motion("", 0);
            }
            setEkspresiManual("netral");
        });
    }

    if (form) {
        form.addEventListener('submit', function(event) {
            // event.preventDefault(); // TIDAK PERLU preventDefault jika ingin memuat ulang halaman

            window.speechSynthesis.cancel(); // Hentikan suara Haru jika sedang bicara

            showLoadingOverlay(); // Tampilkan overlay loading
            
            submitButton.disabled = true;
            submitButton.textContent = 'Memproses...';
            submitButton.classList.add('loading-state');

            if (window.live2dModel) {
                window.live2dModel.motion("", 6); // Gerakan berpikir
            }

            // form.submit() akan dipanggil setelah event listener ini selesai
            // tidak perlu setTimeout di sini
        });
    }

    // Reset button state if user navigates back via browser history
    window.addEventListener('pageshow', (event) => {
        if (event.persisted) { // Check if page was loaded from cache
            hideLoadingOverlay(); // Sembunyikan overlay
            submitButton.disabled = false;
            submitButton.textContent = '💬 Tanyakan ke Haru'; 
            submitButton.classList.remove('loading-state');
            
            questionBoxContainer.style.display = 'none';
            showQuestionBoxBtn.style.display = 'block';
            if (micButtonFixed) {
                micButtonFixed.style.display = 'block';
                micButtonFixed.disabled = false;
            }
            if (micButtonForm) {
                micButtonForm.textContent = '🎤 Tanya Lewat Suara';
                micButtonForm.disabled = false;
            }
            // Juga reset Haru dan bubble
            hideHaruBubble();
            clearInterval(lipSyncInterval);
            if (window.live2dModel) {
                const model = window.live2dModel.internalModel.coreModel;
                model.setParameterValueById("ParamMouthOpenY", 0);
                window.live2dModel.motion("", 0);
            }
            setEkspresiManual("netral");
        }
    });


    // Logic untuk menampilkan hasil dan Haru bicara (ini akan tetap sama)
    window.addEventListener('DOMContentLoaded', () => {
        const jawabanElemen = document.querySelectorAll(".content-text");
        const bubble = document.getElementById("haru-bubble");

        // Pastikan overlay disembunyikan saat halaman dimuat (baik dari fresh load atau post-submit)
        hideLoadingOverlay(); 

        if (jawabanElemen.length > 0) {
            // Show the question box if there's an answer (after form submission)
            questionBoxContainer.style.display = 'block';
            showQuestionBoxBtn.style.display = 'none';
            if (micButtonFixed) { 
                micButtonFixed.style.display = 'none';
            }

            const teks = jawabanElemen[0].textContent.trim();
            const teksLower = teks.toLowerCase();

            speechUtterance = new SpeechSynthesisUtterance(teks);
            const msg = speechUtterance;
            msg.lang = "id-ID";
            msg.rate = 1;

            bubble.textContent = "";
            bubble.style.display = "block";
            bubble.scrollTop = 0;

            // Deteksi ekspresi
            if (teksLower.includes("penjara") || teksLower.includes("tersangka") || teksLower.includes("ditahan")) {
                setEkspresiManual("sedih");
            } else if (teksLower.includes("bebas") || teksLower.includes("tidak bersalah") || teksLower.includes("dihentikan")) {
                setEkspresiManual("senang");
            } else {
                setEkspresiManual("netral");
            }

            let typingInterval = null;
            let charIndex = 0;

            msg.onstart = () => {
                stopButton.style.display = "block";
                if (window.live2dModel) {
                    window.live2dModel.motion("", 7); 
                    lipSyncInterval = setInterval(() => {
                        const open = 0.2 + Math.random() * 0.8;
                        window.live2dModel.internalModel.coreModel.setParameterValueById("ParamMouthOpenY", open);
                    }, 100);
                }

                typingInterval = setInterval(() => {
                    if (charIndex < teks.length) {
                        bubble.textContent += teks.charAt(charIndex);
                        charIndex++;
                        bubble.scrollTop = bubble.scrollHeight;
                    } else {
                        clearInterval(typingInterval);
                    }
                }, 70); 
            };

            msg.onend = () => {
                clearInterval(lipSyncInterval);
                clearInterval(typingInterval);
                stopButton.style.display = "none";
                bubble.style.display = "none"; // Sembunyikan bubble setelah selesai bicara
                if (window.live2dModel) {
                    const model = window.live2dModel.internalModel.coreModel;
                    model.setParameterValueById("ParamMouthOpenY", 0);
                    window.live2dModel.motion("", 0); 
                }

                setEkspresiManual("netral");
            };

            window.speechSynthesis.cancel(); 
            window.speechSynthesis.speak(msg);
        } else {
            // Jika tidak ada hasil, pastikan question box tersembunyi dan tombol terlihat
            questionBoxContainer.style.display = 'none';
            showQuestionBoxBtn.style.display = 'block';
            if (micButtonFixed) { // Pastikan micButtonFixed terlihat jika tidak ada hasil
                micButtonFixed.style.display = 'block';
            }

            // Tampilkan bubble Haru saat halaman dimuat (hanya jika belum ada hasil)
            if (window.live2dModel) {
                setTimeout(() => {
                    showHaruBubble("Halo! Saya Haru, konsultan hukum AI Anda. Ada yang bisa saya bantu?");
                    setTimeout(hideHaruBubble, 5000); 
                }, 1500);
            } else {
                window.addEventListener('live2dModelLoaded', () => {
                    setTimeout(() => {
                        showHaruBubble("Halo! Saya Haru, konsultan hukum AI Anda. Ada yang bisa saya bantu?");
                        setTimeout(hideHaruBubble, 5000);
                    }, 1500);
                });
            }
        }
    });

    function setEkspresiManual(tipe) {
        const model = window.live2dModel?.internalModel?.coreModel;
        if (!model) return;

        if (tipe === "senang") {
            model.setParameterValueById("ParamEyeLOpen", 1);
            model.setParameterValueById("ParamEyeROpen", 1);
            model.setParameterValueById("ParamMouthForm", 1); 
            model.setParameterValueById("ParamBrowLY", 0);
            model.setParameterValueById("ParamBrowRY", 0);
        } else if (tipe === "sedih") {
            model.setParameterValueById("ParamEyeLOpen", 0.6);
            model.setParameterValueById("ParamEyeROpen", 0.6);
            model.setParameterValueById("ParamMouthForm", -0.5); 
            model.setParameterValueById("ParamBrowLY", -0.8); 
            model.setParameterValueById("ParamBrowRY", -0.8);
        } else {
            model.setParameterValueById("ParamEyeLOpen", 1);
            model.setParameterValueById("ParamEyeROpen", 1);
            model.setParameterValueById("ParamMouthForm", 0);
            model.setParameterValueById("ParamBrowLY", 0);
            model.setParameterValueById("ParamBrowRY", 0);
        }
    }
});

