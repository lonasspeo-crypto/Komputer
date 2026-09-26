(() => {
  const form = document.getElementById('classification-form');
  if (!form) return;

  const input = document.getElementById('image-input');
  const dropzone = document.getElementById('dropzone');
  const previewPanel = document.getElementById('preview-panel');
  const previewImage = document.getElementById('dropzone-preview');
  const previewName = document.getElementById('preview-name');
  const previewDetails = document.getElementById('preview-details');
  const qualityPanel = document.getElementById('image-quality');
  const uploadError = document.getElementById('upload-error');
  const submitButton = document.getElementById('submit-btn');
  const loadingIndicator = document.getElementById('loading-indicator');
  const replaceButton = document.getElementById('replace-btn');
  const allowedTypes = ['image/jpeg', 'image/png'];
  const maxFileSize = 10 * 1024 * 1024;
  const minDimension = 224;
  let previewUrl = null;
  let dragDepth = 0;

  const formatFileSize = bytes => `${(bytes / 1024 / 1024).toFixed(1).replace('.', ',')} MB`;

  const showError = message => {
    uploadError.textContent = message;
    uploadError.hidden = false;
    dropzone.hidden = false;
    dropzone.classList.add('has-error');
    form.classList.remove('is-ready');
  };

  const hideError = () => {
    uploadError.textContent = '';
    uploadError.hidden = true;
    dropzone.classList.remove('has-error');
  };

  const revokePreviewUrl = () => {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    previewUrl = null;
  };

  const clearUpload = ({ clearFileInput = true } = {}) => {
    if (clearFileInput) input.value = '';
    revokePreviewUrl();
    previewImage.removeAttribute('src');
    previewPanel.hidden = true;
    qualityPanel.hidden = true;
    dropzone.hidden = false;
    form.classList.remove('is-ready', 'is-analyzing');
    submitButton.disabled = true;
    hideError();
  };

  const readImage = file => new Promise((resolve, reject) => {
    const image = new Image();
    const objectUrl = URL.createObjectURL(file);
    image.onload = () => resolve({ objectUrl, width: image.naturalWidth, height: image.naturalHeight });
    image.onerror = () => {
      URL.revokeObjectURL(objectUrl);
      reject();
    };
    image.src = objectUrl;
  });

  const setInputFile = file => {
    const transfer = new DataTransfer();
    transfer.items.add(file);
    input.files = transfer.files;
  };

  const setQualityText = (id, text) => {
    document.getElementById(id).textContent = text;
  };

  const handleFile = async file => {
    if (!file) return;
    // Keep the selected file in the input while resetting only the visible
    // state. Clearing it here would leave a valid preview with no file to
    // submit to Django.
    clearUpload({ clearFileInput: false });

    if (!allowedTypes.includes(file.type)) {
      showError('Format gambar tidak didukung.\nGunakan JPG atau PNG.');
      return;
    }
    if (file.size > maxFileSize) {
      showError('Ukuran gambar terlalu besar.\nUkuran maksimum 10 MB.');
      return;
    }

    let imageInfo;
    try {
      imageInfo = await readImage(file);
    } catch {
      showError('Gambar tidak dapat dibaca.\nPilih file JPG atau PNG yang valid.');
      return;
    }

    if (imageInfo.width < minDimension || imageInfo.height < minDimension) {
      URL.revokeObjectURL(imageInfo.objectUrl);
      showError('Resolusi gambar rendah.\nGunakan gambar dengan resolusi yang lebih baik.');
      return;
    }

    previewUrl = imageInfo.objectUrl;
    previewImage.src = previewUrl;
    previewName.textContent = file.name;
    previewDetails.textContent = `${formatFileSize(file.size)} • ${imageInfo.width} × ${imageInfo.height} px`;
    setQualityText('quality-format', 'Format sesuai');
    setQualityText('quality-resolution', 'Resolusi cukup');
    setQualityText('quality-size', 'Ukuran file sesuai');
    dropzone.hidden = true;
    previewPanel.hidden = false;
    qualityPanel.hidden = false;
    form.classList.add('is-ready');
    submitButton.disabled = false;
  };

  input.addEventListener('change', () => handleFile(input.files[0]));

  dropzone.addEventListener('keydown', event => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      input.click();
    }
  });

  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, event => event.preventDefault());
  });

  dropzone.addEventListener('dragenter', () => {
    dragDepth += 1;
    dropzone.classList.add('is-dragging');
  });

  dropzone.addEventListener('dragover', () => dropzone.classList.add('is-dragging'));

  dropzone.addEventListener('dragleave', () => {
    dragDepth -= 1;
    if (dragDepth <= 0) {
      dragDepth = 0;
      dropzone.classList.remove('is-dragging');
    }
  });

  dropzone.addEventListener('drop', event => {
    dragDepth = 0;
    dropzone.classList.remove('is-dragging');
    const [file] = event.dataTransfer.files;
    if (!file) return;
    setInputFile(file);
    handleFile(file);
  });

  replaceButton.addEventListener('click', () => input.click());

  form.addEventListener('submit', event => {
    if (!input.files.length) {
      event.preventDefault();
      showError('Pilih gambar primata sebelum memulai identifikasi.');
      return;
    }
    submitButton.disabled = true;
    loadingIndicator.hidden = false;
    form.classList.add('is-analyzing');
    form.setAttribute('aria-busy', 'true');
  });
})();
