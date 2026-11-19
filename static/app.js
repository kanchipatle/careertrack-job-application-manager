// CareerTrack frontend enhancements
document.addEventListener("DOMContentLoaded", () => {
  // Set today's date on a new application form if the field is blank.
  const dateField = document.querySelector('input[name="application_date"]');
  if (dateField && !dateField.value) {
    dateField.value = new Date().toISOString().slice(0, 10);
  }
});
