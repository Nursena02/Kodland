import random
import sys
import pgzrun

# Pencere boyutları
WIDTH = 800
HEIGHT = 400

# Sabitler
ENEMY_SPAWN_OFFSET = 300
GROUND_LEVEL = HEIGHT - 50
PLAYER_KNOCKBACK = 50  # Daha küçük bir değer

# Arka plan resmi
background = "background"

# Oyun durumu
game_state = "MENU"  # MENU, PLAYING
music_enabled = True  # Müzik açık/kapalı
menu_options = ["Start Game", "Toggle Sound", "Quit Game"]
selected_option = 0  # Seçili menü öğesi

# Score ve can değişkenleri
score = 0
lives = 30


class Enemy:
 

    def __init__(self, x, y):
        self.walk_frames = ["enemy_walk1_mid", "enemy_walk2_mid", "enemy_walk3_mid"]
        self.current_frame = 0
        self.actor = Actor(self.walk_frames[self.current_frame])
        self.actor.pos = (x, y)
        self.animation_speed = 8
        self.frame_counter = 0
        self.is_passed = False  # Düşmanın geçilip geçilmediğini takip etmek için

    def draw(self):
      
        self.actor.draw()

    def update(self):
   
        self.actor.x -= 5

        # Düşman ekrandan çıkarsa yeniden oluştur
        if self.actor.x < -50:
            self.actor.x = WIDTH + random.randint(ENEMY_SPAWN_OFFSET, 750)
            self.actor.y = GROUND_LEVEL
            self.is_passed = False  # Yeniden oluşturulduğunda geçilme durumunu sıfırla

        # Animasyon güncelleme
        self.frame_counter += 1
        if self.frame_counter >= self.animation_speed:
            self.frame_counter = 0
            self.current_frame = (self.current_frame + 1) % len(self.walk_frames)
            self.actor.image = self.walk_frames[self.current_frame]


class Player:
  

    def __init__(self):
        self.walk_frames = ["hero_walk1_mid", "hero_walk2_mid", "hero_walk3_mid"]
        self.idle_frames = ["hero_idle1_mid", "hero_idle2_mid", "hero_idle3_mid"]
        self.current_frame = 0
        self.actor = Actor(self.idle_frames[self.current_frame])
        self.actor.pos = (100, GROUND_LEVEL)
        self.speed = 3
        self.jump_power = 15  # Zıplama gücü
        self.gravity = 0.8  # Yer çekimi
        self.velocity = 0  # Dikey hız
        self.is_jumping = False  # Zıplama durumu
        self.animation_speed = 10
        self.frame_counter = 0
        self.is_moving = False  # Hareket durumunu takip etmek için

    def draw(self):

        self.actor.draw()

    def update(self):
   
        if self.is_moving:
            self.frame_counter += 1
            if self.frame_counter >= self.animation_speed:
                self.frame_counter = 0
                self.current_frame = (self.current_frame + 1) % len(self.walk_frames)
                self.actor.image = self.walk_frames[self.current_frame]
        else:
            self.frame_counter += 1
            if self.frame_counter >= self.animation_speed:
                self.frame_counter = 0
                self.current_frame = (self.current_frame + 1) % len(self.idle_frames)
                self.actor.image = self.idle_frames[self.current_frame]

        # Yer çekimi ve zıplama
        self.velocity += self.gravity
        self.actor.y += self.velocity

        # Yere düşmesini engelle 
        if self.actor.y >= GROUND_LEVEL:
            self.actor.y = GROUND_LEVEL
            self.velocity = 0
            self.is_jumping = False

        # Ekranı geçerse başa dönsün 
        if self.actor.x > WIDTH:
            self.actor.x = 0

    def jump(self):
        """Oyuncunun zıplamasını sağlar."""
        if not self.is_jumping:  # Sadece yerdeyken zıplayabilir
            self.velocity = -self.jump_power
            self.is_jumping = True
            sounds.jump.play()  # Zıplama sesi


# Oyun nesneleri
player = Player()
enemies = [Enemy(WIDTH + ENEMY_SPAWN_OFFSET, GROUND_LEVEL), Enemy(WIDTH + 750, GROUND_LEVEL)]


def reset_game():
    """Oyunu sıfırlar ve başlangıç değerlerini yeniden atar."""
    global player, enemies, lives, score
    player = Player()
    enemies = [Enemy(WIDTH + ENEMY_SPAWN_OFFSET, GROUND_LEVEL), Enemy(WIDTH + 750, GROUND_LEVEL)]
    lives = 30
    score = 0


def toggle_sound():
    """Müziği açıp kapatır."""
    global music_enabled
    music_enabled = not music_enabled
    if music_enabled:
        music.play("background_music")
    else:
        music.stop()


def draw_menu():
   
    screen.clear()
    screen.blit(background, (0, 0))
    screen.draw.text("Main Menu", center=(WIDTH // 2, HEIGHT // 4), fontsize=60, color="white")
    
   
    screen.draw.text(f"Last Score: {score}", center=(WIDTH // 2, HEIGHT // 2 - 50), fontsize=40, color="white")

    # Menü seçenekleri
    for i, option in enumerate(menu_options):
        color = "yellow" if i == selected_option else "white"
        screen.draw.text(option, center=(WIDTH // 2, HEIGHT // 2 + i * 50), fontsize=40, color=color)


def draw_game():
    
    screen.clear()
    screen.blit(background, (0, 0))
    player.draw()
    for enemy in enemies:
        enemy.draw()
    screen.draw.text(f"Lives: {lives}", (WIDTH - 100, 10), fontsize=30, color="white")
    screen.draw.text(f"Score: {score}", (10, 10), fontsize=30, color="white")


def update():
   
    global game_state, lives, score

    if game_state == "MENU":
        return

    if game_state == "PLAYING":
        player.update()
        for enemy in enemies:
            enemy.update()
            if player.actor.colliderect(enemy.actor):
                lives -= 1
                sounds.hit.play()  
                print(f"Çarptın! Kalan can: {lives}")
                if lives <= 0:
                    print("Game Over!")
                    game_state = "MENU"
                else:
                    player.actor.x -= PLAYER_KNOCKBACK  # Çarptığında geri atar
                    player.velocity = -player.jump_power  
                    # Karakterin ekran dışına çıkmasını engelle
                    if player.actor.x < 0:
                        player.actor.x = 0

            # Düşmanı geçme kontrolü
            if player.actor.x > enemy.actor.x and not enemy.is_passed:
                score += 10  # Skoru artır
                enemy.is_passed = True  # Düşmanı geçildi olarak işaretle
                sounds.coin.play()  # Skor artışı sesi
                print(f"Skor arttı! Yeni skor: {score}")


def draw():

    if game_state == "MENU":
        draw_menu()
    elif game_state == "PLAYING":
        draw_game()


def on_mouse_down(pos):
    
    global game_state, selected_option
    if game_state == "MENU":
        for i, option in enumerate(menu_options):
            option_rect = Rect(WIDTH // 2 - 100, HEIGHT // 2 + i * 50 - 20, 200, 40)
            if option_rect.collidepoint(pos):
                selected_option = i
                if selected_option == 0:  # Start Game
                    reset_game()
                    game_state = "PLAYING"
                    if music_enabled:
                        music.play("background_music")
                elif selected_option == 1:  # Toggle Sound
                    toggle_sound()
                elif selected_option == 2:  # Quit Game
                    sys.exit()


def on_key_down(key):
    
    global game_state, selected_option
    
    if game_state == "MENU":
        if key == keys.DOWN:
            selected_option = (selected_option + 1) % len(menu_options)
        elif key == keys.UP:
            selected_option = (selected_option - 1) % len(menu_options)
        elif key == keys.RETURN:
            if selected_option == 0:  # Start Game
                reset_game()
                game_state = "PLAYING"
                if music_enabled:
                    music.play("background_music")
            elif selected_option == 1:  # Toggle Sound
                toggle_sound()
            elif selected_option == 2:  # Quit Game
                sys.exit()
    elif game_state == "PLAYING":
        if key == keys.SPACE:
            player.jump()


# Oyunu çalıştır
pgzrun.go()