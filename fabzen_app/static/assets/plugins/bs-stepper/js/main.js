var stepper1
var stepper2
//var stepper3
var stepper4
var stepperForm
const addMoreBankBtn = document.getElementById('add-more-bank');
const form = document.getElementById('companyForm');

 document.addEventListener('DOMContentLoaded', function () {
  // stepper1 = new Stepper(document.querySelector('#stepper1'))
  stepper2 = new Stepper(document.querySelector('#stepper2'), {
    linear: false
  })

  // stepper3 = new Stepper(document.querySelector('#stepper3'))

  var stepperFormEl = document.querySelector('#stepperForm')
  stepperForm = new Stepper(stepperFormEl, {
    animation: true
  })

  var btnNextList = [].slice.call(document.querySelectorAll('.btn-next-form'))
  var stepperPanList = [].slice.call(stepperFormEl.querySelectorAll('.bs-stepper-pane'))
  var inputMailForm = document.getElementById('inputMailForm')
  var inputPasswordForm = document.getElementById('inputPasswordForm')
  var form = stepperFormEl.querySelector('.bs-stepper-content form')

  btnNextList.forEach(function (btn) {
    btn.addEventListener('click', function () {
      stepperForm.next()
    })
  })

  stepperFormEl.addEventListener('show.bs-stepper', function (event) {
    form.classList.remove('was-validated')
    var nextStep = event.detail.indexStep
    var currentStep = nextStep

    if (currentStep > 0) {
      currentStep--
    }

    var stepperPan = stepperPanList[currentStep]

    if ((stepperPan.getAttribute('id') === 'test-form-1' && !inputMailForm.value.length)
    || (stepperPan.getAttribute('id') === 'test-form-2' && !inputPasswordForm.value.length)) {
      event.preventDefault()
      form.classList.add('was-validated')
    }
  })
})


if (addMoreBankBtn) {
    addMoreBankBtn.addEventListener('click', function() {
      const container = document.getElementById('bank-details-container');
      const bankGroup = document.querySelector('.bank-details-group');
      const newBankGroup = bankGroup.cloneNode(true);
      newBankGroup.querySelectorAll('input').forEach(i => i.value = '');

      const removeBtn = document.createElement('button');
      removeBtn.className = 'btn btn-sm btn-outline-danger position-absolute top-0 end-0 m-1';
      removeBtn.innerHTML = '<i class="bx bx-x"></i>';
      removeBtn.onclick = () => container.removeChild(newBankGroup);

      newBankGroup.style.position = 'relative';
      newBankGroup.appendChild(removeBtn);
      container.appendChild(newBankGroup);
    });
  }



form.addEventListener('submit', e => {
    if (!form.checkValidity()) {
      e.preventDefault();
      e.stopPropagation();
    }
    form.classList.add('was-validated');
});




//  window.nextStep = function () {
//     const currentStep = document.querySelector('.bs-stepper-pane.active');
//     let isValid = true;

//     currentStep.querySelectorAll('[required]').forEach(field => {
//       if (!field.value.trim()) {
//         field.classList.add('is-invalid');
//         isValid = false;
//       } else {
//         field.classList.remove('is-invalid');
//       }
//     });

//     if (isValid) {
//       window.companyStepper.next();
//     }
//   };

//   window.prevStep = function () {
//     window.companyStepper.previous();
//   };



window.nextStep = function () {
    const currentStep = document.querySelector('.bs-stepper-pane.active');
    let isValid = true;

    currentStep.querySelectorAll('[required]').forEach(field => {
      if (!field.value.trim()) {
        field.classList.add('is-invalid');
        isValid = false;
      } else {
        field.classList.remove('is-invalid');
      }
    });

    if (isValid) {
      stepper2.next(); // <- yaha change kiya
    }
};


window.prevStep = function () {
    stepper2.previous(); // <- stepper2 use karo
};
