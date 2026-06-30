const API="http://127.0.0.1:8000";

function token(){

    return localStorage.getItem("oracle_token");
}

function authHeaders(){

    return{

        Authorization:`Bearer ${token()}`
    };
}

async function apiGet(url){

    const res=await fetch(API+url,{
        headers:authHeaders()
    });

    return await res.json();
}

async function apiPost(url,body=null){

    const options={

        method:"POST",

        headers:authHeaders()
    };

    if(body){

        options.headers["Content-Type"]="application/json";

        options.body=JSON.stringify(body);
    }

    const res=await fetch(API+url,options);

    return await res.json();
}