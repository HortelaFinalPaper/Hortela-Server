function error(){
	const url = new URLSearchParams(window.location.search);
	const val = url.get('error');
	
	if (val === '1') {
		const vn = url.get('n');
		alert("Nenhum usuario com o nome de "+vn);
	};
}