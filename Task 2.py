Web VPython 3.2

ball = sphere(pos=vec(25, 25, 0), radius=0.3, color=color.red)
ball.velocity = vec(-1, 0.5, 0)
ball.mass = 5.0
ball.trail = curve(color=ball.color)

scene.camera.follow(ball)

particles = []
velocities = []
no_particles = 10000
particle_mass = 2.0
particle_speed = 5

for i in range(no_particles):
    particles.append(sphere(pos=vec(random()*50, random()*50, 0), radius=0.05))
    theta = random() * 2 * pi
    velocities.append(vec(cos(theta) * particle_speed, sin(theta) * particle_speed, 0))

dt = 0.01
t = 0

while True:
    rate(200)
    
    if t >= 100:
        for i in range(no_particles):
            theta = random() * 2 * pi
            velocities[i] = vec(cos(theta) * particle_speed, sin(theta) * particle_speed, 0)
        t = 0
    
    for i in range(no_particles):
        particles[i].pos += velocities[i] * dt
    
    ball.pos += ball.velocity * dt
    ball.trail.append(pos=ball.pos)
    
    for i in range(no_particles):
        diff = ball.pos - particles[i].pos
        dist = mag(diff)
        min_dist = ball.radius + particles[i].radius
        
        if dist < min_dist and dist > 0:
            n = diff / dist
            
            rel_vel = ball.velocity - velocities[i]
            approaching = dot(rel_vel, n)
            
            if approaching < 0:
                m1 = ball.mass
                m2 = particle_mass
                
                ball.velocity = ball.velocity - (2*m2/(m1+m2)) * dot(ball.velocity - velocities[i], n) * n
                velocities[i] = velocities[i] - (2*m1/(m1+m2)) * dot(velocities[i] - ball.velocity, n) * n
                
                overlap = min_dist - dist
                ball.pos += n * overlap
    
    t += 1
