'''
Simple boxing simulation. FPP. The right hand is supposed to react to the player's physics motion.
Needs a bridge to map sensor's live serial data clasification to keyboard inputs.
'''


import pygame
import math
from OpenGL.GL import *
from OpenGL.GLU import *
import time

class BoxingSimulator:
    def __init__(self):
        pygame.init()
        self.width, self.height = 1024, 768
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF | pygame.OPENGL)
        pygame.display.set_caption("₹10 VR Boxing Simulator")
        
        # Initialize OpenGL
        self.init_opengl()
        
        # Hand positions and rotations (relative to camera)
        self.left_hand_pos = [-0.5, -0.3, -0.8]
        self.right_hand_pos = [0.5, -0.3, -0.8]
        
        # Animation states
        self.right_hand_animation = None
        self.animation_time = 0
        self.animation_duration = 0.5  # seconds
        
        # Clock for timing
        self.clock = pygame.time.Clock()
        
    def init_opengl(self):
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        gluPerspective(60, self.width/self.height, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        
    def draw_cube(self, size=0.1):
        """Draw a simple cube"""
        vertices = [
            [-size, -size, -size], [size, -size, -size], [size, size, -size], [-size, size, -size],
            [-size, -size, size], [size, -size, size], [size, size, size], [-size, size, size]
        ]
        
        faces = [
            [0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4],
            [2, 3, 7, 6], [0, 3, 7, 4], [1, 2, 6, 5]
        ]
        
        glBegin(GL_QUADS)
        for face in faces:
            for vertex in face:
                glVertex3fv(vertices[vertex])
        glEnd()
        
    def draw_ground(self):
        """Draw a simple green ground with checkerboard pattern"""
        # Green ground
        glColor3f(0.2, 0.8, 0.2)
        glBegin(GL_QUADS)
        glVertex3f(-10, -1, -10)
        glVertex3f(10, -1, -10)
        glVertex3f(10, -1, 10)
        glVertex3f(-10, -1, 10)
        glEnd()
        
        # Checkerboard pattern
        glColor3f(0.1, 0.6, 0.1)
        for x in range(-5, 6):
            for z in range(-5, 6):
                if (x + z) % 2 == 0:
                    glBegin(GL_QUADS)
                    glVertex3f(x, -0.99, z)
                    glVertex3f(x+1, -0.99, z)
                    glVertex3f(x+1, -0.99, z+1)
                    glVertex3f(x, -0.99, z+1)
                    glEnd()
    
    def draw_sky(self):
        """Draw a simple blue sky"""
        glDisable(GL_DEPTH_TEST)
        glColor3f(0.5, 0.8, 1.0)
        
        glPushMatrix()
        glLoadIdentity()
        glBegin(GL_QUADS)
        glVertex3f(-1, -1, -1)
        glVertex3f(1, -1, -1)
        glVertex3f(1, 1, -1)
        glVertex3f(-1, 1, -1)
        glEnd()
        glPopMatrix()
        
        glEnable(GL_DEPTH_TEST)
    
    def get_hook_position(self, t):
        """Calculate right hand position for hook punch animation"""
        # Hook motion: starts at rest, swings across body, returns
        if t <= 0.3:  # Wind up
            progress = t / 0.3
            x = 0.5 + 0.2 * progress
            y = -0.3 - 0.1 * progress
            z = -0.8 + 0.2 * progress
        elif t <= 0.7:  # Strike
            progress = (t - 0.3) / 0.4
            x = 0.7 - 1.4 * progress  # Swing across body
            y = -0.4 + 0.2 * progress
            z = -0.6 - 0.3 * progress
        else:  # Return
            progress = (t - 0.7) / 0.3
            x = -0.7 + 1.2 * progress
            y = -0.2 - 0.1 * progress
            z = -0.9 + 0.1 * progress
            
        return [x, y, z]
    
    def get_uppercut_position(self, t):
        """Calculate right hand position for uppercut animation"""
        # Uppercut motion: drops down, then shoots up
        if t <= 0.2:  # Wind down
            progress = t / 0.2
            x = 0.5
            y = -0.3 - 0.4 * progress
            z = -0.8 + 0.1 * progress
        elif t <= 0.6:  # Strike up
            progress = (t - 0.2) / 0.4
            x = 0.5 - 0.2 * progress
            y = -0.7 + 1.2 * progress
            z = -0.7 - 0.4 * progress
        else:  # Return
            progress = (t - 0.6) / 0.4
            x = 0.3 + 0.2 * progress
            y = 0.5 - 0.8 * progress
            z = -1.1 + 0.3 * progress
            
        return [x, y, z]
    
    def update_animation(self, dt):
        """Update hand animation based on current state"""
        if self.right_hand_animation:
            self.animation_time += dt
            
            # Calculate normalized time (0 to 1)
            t = self.animation_time / self.animation_duration
            
            if t >= 1.0:
                # Animation complete
                self.right_hand_animation = None
                self.animation_time = 0
                self.right_hand_pos = [0.5, -0.3, -0.8]  # Reset to default
            else:
                # Update position based on animation type
                if self.right_hand_animation == "hook":
                    self.right_hand_pos = self.get_hook_position(t)
                elif self.right_hand_animation == "uppercut":
                    self.right_hand_pos = self.get_uppercut_position(t)
    
    def start_hook(self):
        """Start hook animation"""
        if not self.right_hand_animation:  # Only if not already animating
            self.right_hand_animation = "hook"
            self.animation_time = 0
    
    def start_uppercut(self):
        """Start uppercut animation"""
        if not self.right_hand_animation:  # Only if not already animating
            self.right_hand_animation = "uppercut"
            self.animation_time = 0
    
    def render(self):
        """Render the 3D scene"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Draw sky background
        self.draw_sky()
        
        # Set up first person view
        glLoadIdentity()
        
        # Draw ground
        self.draw_ground()
        
        # Draw left hand (red cube)
        glPushMatrix()
        glTranslatef(*self.left_hand_pos)
        glColor3f(1.0, 0.3, 0.3)  # Red
        self.draw_cube(0.08)
        glPopMatrix()
        
        # Draw right hand (red cube)
        glPushMatrix()
        glTranslatef(*self.right_hand_pos)
        glColor3f(1.0, 0.2, 0.2)  # Slightly different red
        self.draw_cube(0.08)
        glPopMatrix()
        
        # Draw some reference objects in the distance
        for i in range(3):
            glPushMatrix()
            glTranslatef(i * 2 - 2, 0, -5)
            glColor3f(0.8, 0.8, 0.8)  # Gray
            self.draw_cube(0.2)
            glPopMatrix()
        
        pygame.display.flip()
    
    def handle_input(self):
        """Handle keyboard input"""
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_h]:
            self.start_hook()
        elif keys[pygame.K_u]:
            self.start_uppercut()
    
    def run(self):
        """Main game loop"""
        running = True
        last_time = time.time()
        
        print("₹10 VR Boxing Simulator")
        print("Controls:")
        print("H - Right Hand Hook")
        print("U - Right Hand Uppercut")
        print("ESC - Exit")
        
        while running:
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_h:
                        self.start_hook()
                    elif event.key == pygame.K_u:
                        self.start_uppercut()
            
            # Update animations
            self.update_animation(dt)
            
            # Render scene
            self.render()
            
            # Control frame rate
            self.clock.tick(60)
        
        pygame.quit()

if __name__ == "__main__":
    # Check for required dependencies
    try:
        import pygame
        from OpenGL.GL import *
        from OpenGL.GLU import *
    except ImportError as e:
        print(f"Missing required dependency: {e}")
        print("Install with: pip install pygame PyOpenGL")
        exit(1)
    
    simulator = BoxingSimulator()
    simulator.run()