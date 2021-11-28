function validate1(event){
    v1 = document.getElementById("password").value;
    v2 = document.getElementById("confirm_password").value;
    if (v1!==v2){
        alert('Passwords do not match');
        document.getElementById("form1").reset();
        event.preventDefault();
    }
}
