const API_BASE = window.location.origin;

// Tab Navigation Logic
document.querySelectorAll('.nav-links li').forEach(item => {
    item.addEventListener('click', (e) => {
        // Remove active class from all tabs
        document.querySelectorAll('.nav-links li').forEach(li => li.classList.remove('active'));
        document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));
        
        // Add active class to clicked tab
        const targetId = item.getAttribute('data-target');
        item.classList.add('active');
        document.getElementById(targetId).classList.add('active');
    });
});

// Generic API Runner
async function runApi(endpoint, payload) {
    const tabId = document.querySelector('.nav-links li.active').getAttribute('data-target');
    const resultBoxId = `${endpoint.replace('/', '-')}-result`;
    const resultBox = document.getElementById(resultBoxId);
    const btn = event.currentTarget;
    const originalText = btn.innerHTML;

    // UI Loading State
    btn.innerHTML = `<span class="spinner"></span> Processing...`;
    btn.disabled = true;
    resultBox.classList.remove('hidden');
    resultBox.innerHTML = '<span style="color: var(--text-muted)">Awaiting response from RurTech NIM Cloud...</span>';

    try {
        const response = await fetch(`${API_BASE}/${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        
        if (response.ok) {
            // Syntax Highlight JSON
            resultBox.innerHTML = `<span style="color: var(--success)">Success (200 OK)</span>\n\n${JSON.stringify(data, null, 2)}`;
        } else {
            resultBox.innerHTML = `<span style="color: var(--danger)">Error (${response.status})</span>\n\n${JSON.stringify(data, null, 2)}`;
        }
    } catch (error) {
        resultBox.innerHTML = `<span style="color: var(--danger)">Connection Error:</span> ${error.message}\nMake sure the FastAPI backend is running on ${API_BASE}.`;
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

// Health Check
async function checkHealth() {
    const btn = event.currentTarget;
    const originalText = btn.innerHTML;
    const resultBox = document.getElementById('health-result');

    btn.innerHTML = `<span class="spinner"></span> Checking...`;
    btn.disabled = true;
    resultBox.classList.remove('hidden');

    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();
        resultBox.innerHTML = `<span style="color: var(--success)">Backend is Online</span>\n\n${JSON.stringify(data, null, 2)}`;
    } catch (error) {
        resultBox.innerHTML = `<span style="color: var(--danger)">Backend Offline.</span> Make sure you run 'python main.py' in the backend directory.\nError: ${error.message}`;
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

// Image Upload Special Case
async function uploadImage() {
    const fileInput = document.getElementById('inspect-image-file');
    const resultBox = document.getElementById('inspect-image-result');
    const btn = event.currentTarget;
    const originalText = btn.innerHTML;

    if (!fileInput.files.length) {
        alert("Please select an image file first.");
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    btn.innerHTML = `<span class="spinner"></span> Analysing Image...`;
    btn.disabled = true;
    resultBox.classList.remove('hidden');
    resultBox.innerHTML = '<span style="color: var(--text-muted)">Sending to RurTech Vision Model...</span>';

    try {
        const response = await fetch(`${API_BASE}/inspect/image`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        
        if (response.ok) {
            resultBox.innerHTML = `<span style="color: var(--success)">Success (200 OK)</span>\n\n${JSON.stringify(data, null, 2)}`;
        } else {
            resultBox.innerHTML = `<span style="color: var(--danger)">Error (${response.status})</span>\n\n${JSON.stringify(data, null, 2)}`;
        }
    } catch (error) {
        resultBox.innerHTML = `<span style="color: var(--danger)">Connection Error:</span> ${error.message}`;
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

// Summarise File Upload Pipeline
async function uploadSummariseFile() {
    const fileInput = document.getElementById('summarise-file');
    const typeSelect = document.getElementById('summarise-type');
    const resultBox = document.getElementById('summarise-result');
    const btn = event.currentTarget;
    const originalText = btn.innerHTML;

    if (!fileInput.files.length) {
        alert("Please select a file to upload.");
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('doc_type', typeSelect.value);

    btn.innerHTML = `<span class="spinner"></span> Processing File...`;
    btn.disabled = true;
    resultBox.classList.remove('hidden');
    resultBox.innerHTML = '<span style="color: var(--text-muted)">Extracting text and generating regulatory summary via NIM Cloud...</span>';

    try {
        const response = await fetch(`${API_BASE}/summarise/file`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        
        if (response.ok) {
            resultBox.innerHTML = `<span style="color: var(--success)">Success (200 OK)</span>\n\n${JSON.stringify(data, null, 2)}`;
        } else {
            resultBox.innerHTML = `<span style="color: var(--danger)">Error (${response.status})</span>\n\n${JSON.stringify(data, null, 2)}`;
        }
    } catch (error) {
        resultBox.innerHTML = `<span style="color: var(--danger)">Connection Error:</span> ${error.message}`;
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}
// ---------------------------------------------------------------------------
// Biometric Webcam Pipeline
// ---------------------------------------------------------------------------
let videoStream = null;

document.querySelector('[data-target="biometric-tab"]').addEventListener('click', async () => {
    const videoElement = document.getElementById('webcam-video');
    if (!videoStream && navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        try {
            videoStream = await navigator.mediaDevices.getUserMedia({ video: true });
            videoElement.srcObject = videoStream;
        } catch (err) {
            console.error("Webcam error:", err);
            const res = document.getElementById('biometric-result');
            res.innerHTML = '<span style="color: var(--danger)">Webcam Access Denied or Unavailable. Please allow camera permissions.</span>';
            res.classList.remove('hidden');
        }
    }
});

async function captureAndIdentify() {
    const videoElement = document.getElementById('webcam-video');
    const canvasElement = document.getElementById('webcam-canvas');
    const resultBox = document.getElementById('biometric-result');
    const btn = event.currentTarget;
    const originalText = btn.innerHTML;
    
    // Draw frame
    canvasElement.width = videoElement.videoWidth || 640;
    canvasElement.height = videoElement.videoHeight || 480;
    canvasElement.getContext('2d').drawImage(videoElement, 0, 0);
    
    // Base64
    const dataUrl = canvasElement.toDataURL('image/jpeg');
    const imageBase64 = dataUrl.split(',')[1];
    
    if (!imageBase64) {
        alert("Failed to capture image.");
        return;
    }

    btn.innerHTML = '<span class="spinner"></span> Extracting Facenet...';
    btn.disabled = true;
    resultBox.classList.remove('hidden');
    resultBox.innerHTML = '<span style="color: var(--text-muted)">Running RurTech.ai Biometric Extractor extraction...<br>Tokenizing & verifying Blockchain Registry...<br>Synthesizing context via RurTech.ai Core Engine...</span>';

    try {
        const response = await fetch(`${API_BASE}/biometric/identify`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image_base64: imageBase64 })
        });

        const data = await response.json();
        
        if (response.ok) {
            resultBox.innerHTML = `
                <div style="padding: 16px; background: rgba(34, 197, 94, 0.1); border: 1px solid rgba(34, 197, 94, 0.3); border-radius: 8px; margin-bottom: 15px;">
                    <strong style="color: var(--success); font-size: 16px; display: flex; align-items: center; gap: 8px;"><i class="fa-solid fa-robot"></i> RurTech.ai Core Engine Context:</strong>
                    <p style="margin-top: 10px; font-size: 15px; color: #f8fafc; line-height: 1.5; font-style: italic;">"${data.RurTech.ai Core_contextual_greeting}"</p>
                </div>
                <div style="padding: 16px; background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 8px; margin-bottom: 15px;">
                    <strong style="color: #60a5fa; font-size: 14px;"><i class="fa-brands fa-hive"></i> On-Device Blockchain Registry (Secured)</strong>
                    <div style="margin-top: 8px; font-family: monospace; font-size: 12px; color: #cbd5e1;">
                        Token: ${data.tokenizer_pseudonymisation}<br>
                        TX Hash: ${data.blockchain_registry.transaction_hash}<br>
                        Smart Contract: ${data.blockchain_registry.smart_contract}
                    </div>
                </div>
                <strong style="color: var(--accent);">Backend Diagnostics:</strong>
                <pre style="margin-top: 10px; background: rgba(0,0,0,0.3); padding: 10px; border-radius: 6px; font-size: 11px;">${JSON.stringify(data, null, 2)}</pre>
            `;
        } else {
            resultBox.innerHTML = `<span style="color: var(--danger)">Error (${response.status})</span><br><pre>${JSON.stringify(data, null, 2)}</pre>`;
        }
    } catch (error) {
        resultBox.innerHTML = `<span style="color: var(--danger)">Connection Error:</span> ${error.message}`;
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}


// ---------------------------------------------------------------------------
// Mobile Camera Fallback Pipeline
// ---------------------------------------------------------------------------
async function uploadMobileBiometric(input) {
    if (!input.files || !input.files.length) return;
    const file = input.files[0];
    
    // Read file to base64
    const reader = new FileReader();
    reader.onload = async function(e) {
        const base64Url = e.target.result;
        const imageBase64 = base64Url.split(',')[1];
        
        // Hide webcam video, show canvas with static image
        const videoElement = document.getElementById('webcam-video');
        const canvasElement = document.getElementById('webcam-canvas');
        
        const img = new Image();
        img.onload = async () => {
            canvasElement.width = img.width;
            canvasElement.height = img.height;
            canvasElement.getContext('2d').drawImage(img, 0, 0);
            
            videoElement.style.display = 'none';
            canvasElement.style.display = 'block';
            canvasElement.style.width = '100%';
            canvasElement.style.borderRadius = '8px';
            canvasElement.style.border = '2px solid var(--accent)';
            
            // Re-use identify logic
            await runBiometricIdentification(imageBase64, document.querySelector('button[onclick="document.getElementById(\\'mobile-biometric-file\\').click()"]'));
        };
        img.src = base64Url;
    };
    reader.readAsDataURL(file);
}

// Extracted shared logic for desktop/mobile
async function runBiometricIdentification(imageBase64, btn) {
    const resultBox = document.getElementById('biometric-result');
    const originalText = btn.innerHTML;

    btn.innerHTML = '<span class="spinner"></span> Extracting...';
    btn.disabled = true;
    resultBox.classList.remove('hidden');
    resultBox.innerHTML = '<span style="color: var(--text-muted)">Running RurTech.ai Biometric Extractor extraction...<br>Tokenizing & verifying Blockchain Registry...<br>Synthesizing context via RurTech.ai Core Engine...</span>';

    try {
        const response = await fetch(${API_BASE}/biometric/identify, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image_base64: imageBase64 })
        });

        const data = await response.json();
        
        if (response.ok) {
            resultBox.innerHTML = 
                <div style="padding: 16px; background: rgba(34, 197, 94, 0.1); border: 1px solid rgba(34, 197, 94, 0.3); border-radius: 8px; margin-bottom: 15px;">
                    <strong style="color: var(--success); font-size: 16px; display: flex; align-items: center; gap: 8px;"><i class="fa-solid fa-robot"></i> RurTech.ai Core Engine Context:</strong>
                    <p style="margin-top: 10px; font-size: 15px; color: #f8fafc; line-height: 1.5; font-style: italic;">""</p>
                </div>
                <div style="padding: 16px; background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 8px; margin-bottom: 15px;">
                    <strong style="color: #60a5fa; font-size: 14px;"><i class="fa-brands fa-hive"></i> On-Device Blockchain Registry (Secured)</strong>
                    <div style="margin-top: 8px; font-family: monospace; font-size: 12px; color: #cbd5e1;">
                        Token: <br>
                        TX Hash: <br>
                        Smart Contract: 
                    </div>
                </div>
                <strong style="color: var(--accent);">Backend Diagnostics:</strong>
                <pre style="margin-top: 10px; background: rgba(0,0,0,0.3); padding: 10px; border-radius: 6px; font-size: 11px;"></pre>
            ;
        } else {
            resultBox.innerHTML = <span style="color: var(--danger)">Error ()</span><br><pre></pre>;
        }
    } catch (error) {
        resultBox.innerHTML = <span style="color: var(--danger)">Connection Error:</span> ;
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}


