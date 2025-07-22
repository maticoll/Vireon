const clientId = "916833737676-2eu9kmrbdog7sv2911qroi4ipu60cdjt.apps.googleusercontent.com";
const redirectUri = chrome.identity.getRedirectURL("oauth2callback.html");


const scopes = [
  "https://www.googleapis.com/auth/gmail.readonly",
  "https://www.googleapis.com/auth/gmail.modify",
  "https://www.googleapis.com/auth/userinfo.email",
  "https://www.googleapis.com/auth/userinfo.profile",

];

document.getElementById("connect-btn").addEventListener("click", () => {
  document.getElementById("output").innerText = "Conectando con Gmail...";
  
  const authUrl = `https://accounts.google.com/o/oauth2/auth` +
    `?client_id=${clientId}` +
    `&redirect_uri=${encodeURIComponent(redirectUri)}` +
    `&response_type=token` +
    `&scope=${encodeURIComponent(scopes.join(" "))}` +
    `&include_granted_scopes=true`;

  console.log("Redirect URI generado:", redirectUri);

  chrome.identity.launchWebAuthFlow({
    url: authUrl,
    interactive: true
  }, function (redirectUrl) {
    console.log("Autenticado correctamente");
    console.log("Redirect URL:", redirectUrl);
    if (chrome.runtime.lastError || !redirectUrl) {
      console.error("Error en login:", chrome.runtime.lastError);
      document.getElementById("output").innerText = "Error en la autenticación";
      return;
    }

    const tokenMatch = redirectUrl.match(/access_token=([^&]+)/);
    if (tokenMatch) {
      const token = tokenMatch[1];
      console.log("Token de acceso:", token);

      //obtener el email
      fetch("https://www.googleapis.com/oauth2/v2/userinfo", {
        headers: { Authorization: `Bearer ${token}` }
      })
      .then(res => res.json())
      .then(async userInfo => {
        const email = userInfo.email;
        console.log("Email del usuario:", email);
      
        // Enviar a tu backend para guardarlo en Supabase
        await fetch("https://lldewnvonqnqkrivhmid.supabase.co/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            email: email,
            access_token: token
          })
        });
      
        console.log("Usuario registrado en Supabase.");
      });

      // Enviarlo al background para guardarlo
      chrome.runtime.sendMessage({ type: "SAVE_TOKEN", token });
      document.getElementById("output").innerText = "Conectado exitosamente con Gmail!";
      
      // Obtener mensajes de Gmail
      getGmailMessages(token);
    } else {
      console.error("No se encontró el token en la URL.");
      document.getElementById("output").innerText = "Error: No se pudo obtener el token";
    }
  });
});

// Función para obtener mensajes de Gmail
async function getGmailMessages(token) {
  try {
    document.getElementById("output").innerText = "Obteniendo mensajes...";
    
    const response = await fetch("https://gmail.googleapis.com/gmail/v1/users/me/messages?maxResults=5", {
      headers: { Authorization: `Bearer ${token}` }
    });
    
    if (!response.ok) {
      throw new Error(`Error HTTP: ${response.status}`);
    }
    
    const data = await response.json();
    console.log("Mensajes obtenidos:", data);
    
    // Procesar cada mensaje
    for (const message of data.messages) {
      await getMessageDetails(token, message.id);
    }
    
    document.getElementById("output").innerText = "Mensajes procesados y enviados al webhook!";
    
  } catch (error) {
    console.error("Error obteniendo mensajes:", error);
    document.getElementById("output").innerText = "Error obteniendo mensajes";
  }
}

// Función para obtener detalles de un mensaje específico
async function getMessageDetails(token, messageId) {
  try {
    const response = await fetch(`https://gmail.googleapis.com/gmail/v1/users/me/messages/${messageId}?format=full`, {
      headers: { Authorization: `Bearer ${token}` }
    });

    if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
    
    const messageData = await response.json();
    const headers = messageData.payload.headers;
    const subject = headers.find(h => h.name === "Subject")?.value || "Sin asunto";
    const from = headers.find(h => h.name === "From")?.value || "Desconocido";

    // 🧠 Obtener el cuerpo plano
    const bodyPart = getBodyFromPayload(messageData.payload);
    const decodedBody = atob(bodyPart.replace(/-/g, '+').replace(/_/g, '/'));

    // Enviar al webhook
    await sendToWebhook(subject, decodedBody);

  } catch (error) {
    console.error("Error obteniendo detalles del mensaje:", error);
  }
}

// Función para extraer el cuerpo del mensaje del payload
function getBodyFromPayload(payload) {
  if (payload.body && payload.body.data) {
    return payload.body.data;
  }
  
  if (payload.parts) {
    for (const part of payload.parts) {
      if (part.mimeType === "text/plain") {
        return part.body.data;
      }
      if (part.parts) {
        const nestedBody = getBodyFromPayload(part);
        if (nestedBody) return nestedBody;
      }
    }
  }
  
  return "";
}

// Función para enviar datos al webhook
async function sendToWebhook(subject, decodedBody) {
  try {
    const response = await fetch("https://hook.us2.make.com/vh2644shvy4dvq8kaq854ou7b8fqnzf0", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        subject,
        body: decodedBody
      })
    });
    
    if (!response.ok) {
      throw new Error(`Error HTTP: ${response.status}`);
    }
    
    console.log("Datos enviados al webhook para asunto:", subject);
    
  } catch (error) {
    console.error("Error enviando al webhook:", error);
  }
}
