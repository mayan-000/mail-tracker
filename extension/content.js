function addCTAButton() {
  if (document.getElementById("cta-button")) {
    return;
  }

  const sendContainer = document.querySelector(".btC");

  if (!sendContainer) {
    console.error("Send button not found");
    return;
  }

  const button = document.createElement("button");
  button.id = "cta-button";
  button.textContent = "Track Email";
  button.style.marginLeft = "10px";
  button.style.marginRight = "95px";
  button.style.padding = "5px 10px";
  button.style.backgroundColor = "#4285f4";
  button.style.color = "#fff";
  button.style.border = "none";
  button.style.borderRadius = "5px";
  button.style.cursor = "pointer";

  button.addEventListener("click", () => {
    const subjectElement = document.querySelector('input[name="subjectbox"]');
    const toElement =
      document.querySelector(".oL.aDm.az9").childNodes[0].textContent;
    const fromElement = document.querySelector(".gb_A.gb_Xa.gb_Z");

    if (!subjectElement || !toElement || !fromElement) {
      console.error("Subject, To, or From field not found");
      return;
    }

    const subject = subjectElement.value;
    const receiver_email = toElement;
    const from_email = fromElement
      .getAttribute("aria-label")
      .split("(")[1]
      .split(")")[0];

    chrome.runtime.sendMessage(
      {
        action: "createTracker",
        data: {
          receiver_email,
          subject,
          from_email,
        },
      },
      (response) => {
        injectTrackingPixel(response.tracking_url);
      }
    );
  });

  sendContainer.appendChild(button);
}

function injectTrackingPixel(tracking_url) {
  const composeBox = document.querySelector(".Am.Al.editable.LW-avf.tS-tW");
  if (composeBox) {
    const trackingPixel = `<img src="${tracking_url}" width="1" height="1" style="display:none;">`;
    composeBox.innerHTML += trackingPixel;
  } else {
    console.error("Compose box not found");
  }
}

const observer = new MutationObserver(() => {
  const composeBox = document.querySelector(".Am.Al.editable.LW-avf.tS-tW");
  if (composeBox) {
    addCTAButton();
  }
});

observer.observe(document.body, { childList: true, subtree: true });
