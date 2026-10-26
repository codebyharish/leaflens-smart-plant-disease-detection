const input = document.getElementById('leaf-image');
const zone = document.getElementById('dropzone');
const previewRow = document.getElementById('preview-row');
if (input) {
  const show = file => { if (!file) return; document.getElementById('preview').src = URL.createObjectURL(file); document.getElementById('file-name').textContent = file.name; previewRow.hidden = false; };
  input.addEventListener('change', e => show(e.target.files[0]));
  ['dragenter','dragover'].forEach(event => zone.addEventListener(event, e => {e.preventDefault(); zone.classList.add('drag');}));
  ['dragleave','drop'].forEach(event => zone.addEventListener(event, e => {e.preventDefault(); zone.classList.remove('drag');}));
  zone.addEventListener('drop', e => { input.files = e.dataTransfer.files; show(e.dataTransfer.files[0]); });
}
