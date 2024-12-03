chrome.runtime.onMessage.addListener((message, _, sendResponse) => {
  if (message.action === "createTracker") {
    const { from_email, receiver_email, subject } = message.data;

    fetch("http://127.0.0.1:5000/create-tracker", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ from_email, receiver_email, subject }),
    })
      .then((response) => {
        console.log(response);
        if (!response.ok) {
          throw new Error("Failed to create tracking ID");
        }

        return response.json();
      })
      .then((data) => {
        if (data.status === "success") {
          console.log("Tracking ID created:", data.message_id);

          sendResponse({
            tracking_url: `http://127.0.0.1:5000/track/${data.message_id}.png`,
          });
        } else {
          console.error("Error creating tracking ID:", data.message);
        }
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }

  return true;
});
