

  document.addEventListener('DOMContentLoaded', function() {
  const container = document.getElementById('bank-details-container');
  const addBtn = document.getElementById('add-more-bank');

  addBtn.addEventListener('click', () => {
    const original = container.querySelector('.bank-details-group');
    const clone = original.cloneNode(true);

    // Clear input values
    clone.querySelectorAll('input').forEach(inp => inp.value = '');

    // Show remove button for cloned group
    const removeBtn = clone.querySelector('.remove-bank');
    removeBtn.style.display = 'inline-block';

    // Attach remove functionality
    removeBtn.addEventListener('click', () => {
      clone.remove();
    });

    container.appendChild(clone);
  });

  // Keep the first remove button hidden
  const firstRemoveBtn = container.querySelector('.bank-details-group .remove-bank');
  if (firstRemoveBtn) firstRemoveBtn.style.display = 'none';

  window.companyStepper = new Stepper(document.querySelector('#companyStepper'));
});


