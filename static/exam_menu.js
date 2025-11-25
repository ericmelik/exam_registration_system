const form = document.getElementById('examForm');
const appointmentsList = document.getElementById('appointmentsList');
const emptyState = document.getElementById('emptyState');

form.addEventListener('submit', (e) => {
  e.preventDefault();

  const name = document.getElementById('search1').value.trim() || 'N/A';
  const time = document.getElementById('time').value;
  const date = document.getElementById('date').value;
  const examType = document.getElementById('examType').value;
  const subject = document.getElementById('subject').value;
  const location = document.querySelector('input[name="location"]:checked').value;

  if (!time || !date || !examType || !subject) {
    alert('Please fill out all required fields.');
    return;
  }

  emptyState.style.display = 'none';
  appointmentsList.style.display = 'block';

  const appointment = document.createElement('div');
  appointment.classList.add('appointment-item');

  appointment.innerHTML = `
    <button class="cancel-btn">Cancel</button>
    <h3>${examType.charAt(0).toUpperCase() + examType.slice(1)}</h3>
    <p><strong>Name/ID:</strong> ${name}</p>
    <p><strong>Subject:</strong> ${subject.charAt(0).toUpperCase() + subject.slice(1)}</p>
    <p><strong>Date:</strong> ${date}</p>
    <p><strong>Time:</strong> ${time}</p>
    <p><strong>Location:</strong> ${location}</p>
  `;

  appointment.querySelector('.cancel-btn').addEventListener('click', () => {
    appointment.remove();
    if (appointmentsList.children.length === 0) {
      appointmentsList.style.display = 'none';
      emptyState.style.display = 'block';
    }
  });

  appointmentsList.appendChild(appointment);
  form.reset();
  alert('Exam scheduled successfully!');
});