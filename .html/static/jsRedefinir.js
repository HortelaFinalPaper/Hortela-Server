function codeV(){
	cod = document.getElementById("code").value;
	cod2 = document.getElementById("code2").textContent;
	input = document.getElementById("input")
	
	if(cod == cod2){
		input.disabled = false
	}else{
		alert("Código incorreto")
		input.disabled = true
	}
}
function error(){
	const url = new URLSearchParams(window.location.search);
	const val = url.get('error');

	if (val === '1') {
		alert("Conta não existente")
	}
}
function verifyCod(){
	cod2 = document.getElementById("code2").textContent;
	
	if(cod2 == ""){
		window.location.href = "/login";
	}
}