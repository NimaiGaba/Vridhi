
// Your 3D scene setup here...
if ('scrollRestoration' in history) {
  history.scrollRestoration = 'manual';
}
gsap.registerPlugin(ScrollTrigger);

// Using Locomotive Scroll from Locomotive https://github.com/locomotivemtl/locomotive-scroll

const locoScroll = new LocomotiveScroll({
  el: document.querySelector("#main"),
  smooth: true
});
// each time Locomotive Scroll updates, tell ScrollTrigger to update too (sync positioning)
locoScroll.on("scroll", ScrollTrigger.update);

// tell ScrollTrigger to use these proxy methods for the "#main" element since Locomotive Scroll is hijacking things
ScrollTrigger.scrollerProxy("#main", {
  scrollTop(value) {
    return arguments.length ? locoScroll.scrollTo(value, 0, 0) : locoScroll.scroll.instance.scroll.y;
  }, // we don't have to define a scrollLeft because we're only scrolling vertically.
  getBoundingClientRect() {
    return { top: 0, left: 0, width: window.innerWidth, height: window.innerHeight };
  },
  // LocomotiveScroll handles things completely differently on mobile devices - it doesn't even transform the container at all! So to get the correct behavior and avoid jitters, we should pin things with position: fixed on mobile. We sense it by checking to see if there's a transform applied to the container (the LocomotiveScroll-controlled element).
  pinType: document.querySelector("#main").style.transform ? "transform" : "fixed"
});
// each time the window updates, we should refresh ScrollTrigger and then update LocomotiveScroll. 
ScrollTrigger.addEventListener("refresh", () => locoScroll.update());

// after everything is set up, refresh() ScrollTrigger and update LocomotiveScroll because padding may have been added for pinning, etc.
ScrollTrigger.refresh();



document.querySelectorAll('nav a').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    e.preventDefault();
    const targetId = this.getAttribute('href');
    const targetSection = document.querySelector(targetId);
    if (targetSection) {
      locoScroll.scrollTo(targetSection);
      history.replaceState(null, null, ' ');
    }
  });
});
    
   
    document.querySelectorAll('.feature-card').forEach((card, index) => {
      card.style.transitionDelay = `${index * 0.1}s`;
    });
    
    
    function resizeVideo() {
      const video = document.querySelector('.video-bg');
      const aspectRatio = 16/9;
      
      if (window.innerWidth / window.innerHeight > aspectRatio) {
        video.style.width = '100%';
        video.style.height = 'auto';
      } else {
        video.style.width = 'auto';
        video.style.height = '100%';
      }
    }
    
// Toggle chatbot visibility
function toggleChat() {
  const chat = document.getElementById('chatWindow');
  chat.style.display = chat.style.display === 'flex' ? 'none' : 'flex';
}

// Submit message on Enter (not Shift+Enter)
document.getElementById('userInput').addEventListener('keydown', function (e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

// Send message function
async function sendMessage() {
  const input = document.getElementById('userInput');
  const chatBody = document.getElementById('chatBody');
  const typingIndicator = document.getElementById('typingIndicator');

  const rawMessage = input.value.trim();
  if (rawMessage === '') return;

  // Replace newline characters with <br>
  const messageHTML = rawMessage.replace(/\n/g, '<br>');

  // Create user message bubble
  const userMsg = document.createElement('div');
  userMsg.classList.add('chat-message', 'user');
  userMsg.innerHTML = messageHTML;
  chatBody.appendChild(userMsg);

  input.value = '';
  chatBody.scrollTop = chatBody.scrollHeight;

  // Show typing indicator
  typingIndicator.style.display = 'block';

  try {
    const response = await fetch('http://127.0.0.1:8000/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ message: rawMessage })
    });

    const data = await response.json();
    console.log("✅ Server response:", data);
    typingIndicator.style.display = 'none';

    const botMsg = document.createElement('div');
    botMsg.classList.add('chat-message', 'bot');

    if (data.reply) {
      botMsg.innerHTML = data.reply.replace(/\n/g, '<br>');
    } else {
      botMsg.innerHTML = `⚠️ Unexpected server response.`;
    }

    chatBody.appendChild(botMsg);
    chatBody.scrollTop = chatBody.scrollHeight;

  } catch (error) {
    typingIndicator.style.display = 'none';
    const errorMsg = document.createElement('div');
    errorMsg.classList.add('chat-message', 'bot');
    errorMsg.innerHTML = `❌ Server error. Try again later.`;
    chatBody.appendChild(errorMsg);
    chatBody.scrollTop = chatBody.scrollHeight;
    console.error('❌ Fetch error:', error);
  }
}



const canvas = document.querySelector("canvas");
const context = canvas.getContext("2d");

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;


window.addEventListener("resize", function () {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  render();
});

function files(index) {
  const frameNumber = (index + 1).toString().padStart(3, '0'); // "001", "002", etc.
  return `/static/frames/ezgif-frame-${frameNumber}.jpg`;
}

const frameCount = 160;


const images = [];
const imageSeq = {
  frame: 1,
};

for (let i = 0; i < frameCount; i++) {
  const img = new Image();
  img.src = files(i);
  images.push(img);
}

gsap.to(imageSeq, {
  frame: frameCount - 1,
  snap: "frame",
  ease: `none`,
  scrollTrigger: {
    scrub: 0.15,
    trigger: `#page>canvas`,
    start: `top top`,
    end: `300% top`,
    scroller: `#main`,
  },
  onUpdate: render,
});

images[1].onload = render;

function render() {
  scaleImage(images[imageSeq.frame], context);
}

function scaleImage(img, ctx) {
  var canvas = ctx.canvas;
  var hRatio = canvas.width / img.width;
  var vRatio = canvas.height / img.height;
  var ratio = Math.max(hRatio, vRatio);
  var centerShift_x = (canvas.width - img.width * ratio) / 2;
  var centerShift_y = (canvas.height - img.height * ratio) / 2;
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.drawImage(
    img,
    0,
    0,
    img.width,
    img.height,
    centerShift_x,
    centerShift_y,
    img.width * ratio,
    img.height * ratio
  );
}
ScrollTrigger.create({
  trigger: "#page>canvas",
  pin: true,
  // markers:true,
  scroller: `#main`,
  start: `top top`,
  end: `300% top`,
});

// About modal functionality
const aboutModal = document.getElementById('aboutModal');
const aboutButton = document.querySelector('nav a[href="#about"]');
const closeModal = document.querySelector('.close-modal');

function openAboutModal() {
  aboutModal.style.display = 'flex';
  setTimeout(() => {
    aboutModal.classList.add('active');
  }, 10);
  
  // Pause Locomotive Scroll while modal is open
  locoScroll.stop();
}

function closeAboutModal() {
  aboutModal.classList.remove('active');
  setTimeout(() => {
    aboutModal.style.display = 'none';
  }, 600); // Match this with your CSS transition duration
  
  // Resume Locomotive Scroll
  locoScroll.start();
}

aboutButton.addEventListener('click', (e) => {
  e.preventDefault();
  openAboutModal();
});

closeModal.addEventListener('click', closeAboutModal);

// Close modal when clicking outside content
aboutModal.addEventListener('click', (e) => {
  if (e.target === aboutModal || e.target === document.querySelector('.modal-overlay')) {
    closeAboutModal();
  }
});