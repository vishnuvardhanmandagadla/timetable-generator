const canvas = document.getElementById('energyCanvas');
const ctx = canvas.getContext('2d');

let width, height, particles = [];

function initCanvas() {
    canvas.width = width = window.innerWidth;
    canvas.height = height = window.innerHeight;
    createParticles();
}

function createParticles() {
    particles = [];
    for (let i = 0; i < 500; i++) {  // Increase the number of particles
        particles.push(new Particle());
    }
}

function Particle() {
    this.x = Math.random() * width;
    this.y = Math.random() * height;
    this.vx = (Math.random() - 0.5) * 2;
    this.vy = (Math.random() - 0.5) * 2;
    this.size = Math.random() * 1.5 + 0.5;  // Decrease the size of particles
    this.color = `hsl(${Math.random() * 360}, 100%, 50%)`;

    this.update = function() {
        this.x += this.vx;
        this.y += this.vy;

        if (this.x < 0 || this.x > width) this.vx *= -1;
        if (this.y < 0 || this.y > height) this.vy *= -1;
    };

    this.draw = function() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fillStyle = this.color;
        ctx.fill();
    };
}

function animate() {
    ctx.clearRect(0, 0, width, height);
    particles.forEach(p => {
        p.update();
        p.draw();
    });
    requestAnimationFrame(animate);
}

window.addEventListener('resize', initCanvas);
window.addEventListener('mousemove', (e) => {
    particles.forEach(p => {
        const dx = e.clientX - p.x;
        const dy = e.clientY - p.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        if (distance < 100) {
            const angle = Math.atan2(dy, dx);
            p.vx += Math.cos(angle) * 0.5;
            p.vy += Math.sin(angle) * 0.5;
        }
    });
});

initCanvas();
animate();
