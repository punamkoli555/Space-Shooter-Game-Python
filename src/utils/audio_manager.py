import pygame
import os
import numpy as np
from typing import Dict, Optional
from game.settings import Settings
from utils.debug_utils import debug_print

class AudioManager:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.audio_enabled = True
        
        # Initialize pygame mixer
        try:
            pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
            pygame.mixer.init()
            debug_print("🔊 Audio system initialized")
        except pygame.error as e:
            debug_print(f"❌ Audio initialization failed: {e}")
            self.audio_enabled = False
            return
        
        self.master_volume = 0.7
        self.music_volume = 0.6
        self.sfx_volume = 0.8
        self.sound_volume = self.sfx_volume
        self.menu_music_volume = 0.5
        self.game_music_volume = 0.6
        
        # Music state
        self.current_music = None
        self.is_fading = False
        self.fade_target_volume = 0
        self.fade_speed = 0
        
        # Sound effects cache
        self.sounds = {}
        
        # Load sounds immediately
        self.load_sounds()
        
        debug_print("🔊 Audio manager initialized")
    
    def initialize_audio(self):
        """Initialize pygame audio system."""
        try:
            # Check if mixer is already initialized
            if pygame.mixer.get_init() is None:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
            
            # Set volumes
            pygame.mixer.music.set_volume(self.music_volume)
            
            debug_print("✅ Audio system initialized successfully")
            
        except pygame.error as e:
            debug_print(f"⚠️ Audio initialization failed: {e}")
            self.audio_enabled = False
    
    def load_sounds(self):
        """Load game sound effects."""
        if not self.audio_enabled:
            debug_print("⚠️ Audio disabled, creating silent placeholders")
            self.create_silent_sounds()
            return
        
        sound_files = {
            'shoot': 'shoot.wav',
            'explosion': 'explosion.wav', 
            'powerup': 'powerup.wav',
            'enemy_hit': 'enemy_hit.wav',
            'player_hit': 'player_hit.wav',
            'menu_select': 'menu_select.wav',
            'menu_navigate': 'menu_navigate.wav',
            'boss_spawn': 'boss_spawn.wav',
            'level_up': 'level_up.wav',
            'menu_move': 'menu_navigate.wav',
            'menu_confirm': 'menu_select.wav',
            'menu_back': 'menu_navigate.wav'
        }
        
        sounds_path = "assets/sounds"
        sounds_loaded = 0
        
        for sound_name, filename in sound_files.items():
            file_path = os.path.join(sounds_path, filename)
            
            if os.path.exists(file_path):
                try:
                    sound = pygame.mixer.Sound(file_path)
                    sound.set_volume(self.sfx_volume)
                    self.sounds[sound_name] = sound
                    debug_print(f"✅ Loaded sound: {sound_name} -> {filename}")
                    sounds_loaded += 1
                except pygame.error as e:
                    debug_print(f"❌ Failed to load {sound_name} from {filename}: {e}")
                    self.create_placeholder_sound(sound_name)
            else:
                debug_print(f"⚠️ Sound file not found: {file_path}")
                # Check if the file exists with different extension
                base_name = filename.split('.')[0]
                for ext in ['.wav', '.mp3', '.ogg']:
                    alt_path = os.path.join(sounds_path, base_name + ext)
                    if os.path.exists(alt_path):
                        try:
                            sound = pygame.mixer.Sound(alt_path)
                            sound.set_volume(self.sfx_volume)
                            self.sounds[sound_name] = sound
                            debug_print(f"✅ Loaded sound: {sound_name} -> {base_name + ext} (fallback)")
                            sounds_loaded += 1
                            break
                        except pygame.error as e:
                            debug_print(f"❌ Failed to load fallback {sound_name}: {e}")
                            continue
                else:
                    # No file found, create placeholder
                    debug_print(f"Creating placeholder for {sound_name}")
                    self.create_placeholder_sound(sound_name)
        
        if sounds_loaded == 0:
            debug_print("⚠️ No sound files loaded, using placeholders")
        else:
            debug_print(f"🔊 Loaded {sounds_loaded}/{len(sound_files)} sound files")
    
    def create_silent_sounds(self):
        """Create silent placeholder sounds when audio is disabled."""
        sound_names = ['shoot', 'explosion', 'powerup', 'enemy_hit', 'player_hit', 
                      'menu_select', 'menu_navigate', 'boss_spawn', 'level_up',
                      'menu_move', 'menu_confirm', 'menu_back']
        
        for sound_name in sound_names:
            # Create a very short silent sound instead of None
            try:
                # Create 0.1 second silent sound
                silent_array = np.zeros((int(44100 * 0.1), 2), dtype=np.int16)
                sound = pygame.sndarray.make_sound(silent_array)
                sound.set_volume(0)  # Ensure it's silent
                self.sounds[sound_name] = sound
            except:
                # If even that fails, create minimal silent sound
                try:
                    minimal_sound = pygame.mixer.Sound(buffer=np.zeros((1000, 2), dtype=np.int16))
                    minimal_sound.set_volume(0)
                    self.sounds[sound_name] = minimal_sound
                except:
                    # Last resort: skip this sound entirely and handle in play_sound
                    debug_print(f"⚠️ Cannot create sound for {sound_name}, will skip during playback")
                    continue
                
        debug_print("🔇 Created silent placeholder sounds")
    
    def create_placeholder_sound(self, sound_name: str):
        """Create simple beep sounds as placeholders."""
        try:
            # Create a short sound array
            sample_rate = 22050
            duration = 0.2  # 0.2 seconds
            frames = int(duration * sample_rate)
            arr = np.zeros((frames, 2), dtype=np.int16)
            
            # Different frequencies for different sounds
            if sound_name in ['shoot']:
                frequency = 800
            elif sound_name in ['explosion']:
                frequency = 150
            elif sound_name in ['powerup', 'level_up']:
                frequency = 600
            elif sound_name in ['menu_navigate', 'menu_move']:
                frequency = 400
            elif sound_name in ['menu_select', 'menu_confirm', 'menu_back']:
                frequency = 500
            else:
                frequency = 440
            
            for i in range(frames):
                wave = 1000 * np.sin(2 * np.pi * frequency * i / sample_rate)
                envelope = max(0, 1.0 - (i / frames))  # Fade out
                arr[i] = [int(wave * envelope), int(wave * envelope)]
            
            sound = pygame.sndarray.make_sound(arr)
            sound.set_volume(self.sfx_volume * 0.3)  # Quieter placeholders
            self.sounds[sound_name] = sound
            debug_print(f"🔊 Created placeholder sound: {sound_name}")
            
        except Exception as e:
            debug_print(f"❌ Failed to create placeholder for {sound_name}: {e}")
            # Create a minimal silent sound as last resort
            try:
                silent_array = np.zeros((1000, 2), dtype=np.int16)
                sound = pygame.sndarray.make_sound(silent_array)
                sound.set_volume(0)
                self.sounds[sound_name] = sound
            except:
                self.sounds[sound_name] = None
    
    def play_sound(self, sound_name: str, volume: float = 1.0):
        """Play a sound effect."""
        if not self.audio_enabled:
            return
        
        # Check if sound exists before trying to play
        if sound_name in self.sounds:
            sound = self.sounds[sound_name]
            if sound is not None:
                try:
                    sound.set_volume(self.sound_volume * volume)
                    sound.play()
                    debug_print(f"🔊 Playing sound: {sound_name}")
                except pygame.error as e:
                    debug_print(f"❌ Error playing sound {sound_name}: {e}")
        else:
            debug_print(f"⚠️ Sound not found: {sound_name}")
            
    def play_splash_music(self):
        """Play splash screen music."""
        if not self.audio_enabled:
            return
        
        # Stop any current music
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        
        # Try to load splash music files
        splash_music_files = [
            'splashscreen_music.mp3',
            'splash_music.mp3',
            'splash_music.ogg',
            'splash_music.wav'
        ]
        
        for music_file in splash_music_files:
            music_path = os.path.join("assets/sounds", music_file)
            if os.path.exists(music_path):
                try:
                    pygame.mixer.music.load(music_path)
                    pygame.mixer.music.set_volume(self.music_volume * 0.8)
                    pygame.mixer.music.play(-1)  # Loop during splash
                    self.current_music = 'splash'
                    debug_print(f"🎵 Playing splash music: {music_file}")
                    return
                except pygame.error as e:
                    debug_print(f"❌ Error loading splash music {music_file}: {e}")
                    continue
        
        debug_print("⚠️ No splash music files found, splash will be silent")

    def stop_splash_music(self, fade_time: float = 1.0):
        """Stop splash music with fade out."""
        if not self.audio_enabled or self.current_music != 'splash':
            return
        
        debug_print("🎵 Fading out splash music...")
        self.fade_out_music(fade_time)
        
        # Set timer to clear music state after fade
        pygame.time.set_timer(pygame.USEREVENT + 4, int(fade_time * 1000 + 100))

    def handle_splash_music_event(self, event):
        """Handle splash music timing events."""
        if event.type == pygame.USEREVENT + 4:
            # Clear splash music state after fade out
            if self.current_music == 'splash':
                self.current_music = None
                debug_print("🎵 Splash music stopped")
            pygame.time.set_timer(pygame.USEREVENT + 4, 0)  # Cancel timer
    
    def play_menu_sound(self, action: str):
        """Play menu-specific sounds."""
        sound_map = {
            'navigate': 'menu_move',
            'select': 'menu_confirm', 
            'back': 'menu_back',
            'move': 'menu_move',
            'confirm': 'menu_confirm'
        }
        
        sound_name = sound_map.get(action, 'menu_select')
        self.play_sound(sound_name, 0.8)  # Slightly quieter for menus
        
    
    def play_menu_music(self):
        """Play menu background music."""
        if not self.audio_enabled:
            return
        
        # Stop current music if different
        if self.current_music != 'menu':
            self.stop_music()
        
        # Try to load menu music files
        menu_music_files = [
            'menu_music.mp3',
            'menu_music.ogg',
            'menu_music.wav'
        ]
        
        for music_file in menu_music_files:
            music_path = os.path.join("assets/sounds", music_file)
            if os.path.exists(music_path):
                try:
                    pygame.mixer.music.load(music_path)
                    pygame.mixer.music.set_volume(self.menu_music_volume)
                    pygame.mixer.music.play(-1)  # Loop infinitely
                    self.current_music = 'menu'
                    debug_print(f"🎵 Playing menu music: {music_file}")
                    return
                except pygame.error as e:
                    debug_print(f"❌ Error loading menu music {music_file}: {e}")
                    continue
        
        debug_print("⚠️ No menu music files found")
    
    def play_game_music(self, fade_in_time: float = 2.5):
        """Play game background music with fade-in - FIXED interruption issues."""
        if not self.audio_enabled:
            debug_print("⚠️ Audio disabled, skipping game music")
            return
        
        debug_print(f"🎵 Starting game music with {fade_in_time}s fade-in...")
        
        # Stop any existing music and clear state
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            debug_print("🎵 Stopped existing music before starting game music")
        
        # Clear any ongoing fade operations
        self.is_fading = False
        
        # Try to load game music files
        game_music_files = [
            'background_music.wav',
            'game_music.ogg',
            'game_music.mp3', 
            'game_music.wav'
        ]
        
        music_loaded = False
        for music_file in game_music_files:
            music_path = os.path.join("assets/sounds", music_file)
            if os.path.exists(music_path):
                try:
                    # Load and start the music
                    pygame.mixer.music.load(music_path)
                    
                    # Start with low volume for fade-in
                    start_volume = 0.1  # Start slightly above 0 to avoid mixer issues
                    pygame.mixer.music.set_volume(start_volume)
                    pygame.mixer.music.play(-1)  # Loop infinitely
                    
                    # Verify music actually started
                    if pygame.mixer.music.get_busy():
                        # Set up smooth fade-in
                        self.is_fading = True
                        self.fade_target_volume = self.game_music_volume
                        self.fade_speed = (self.game_music_volume - start_volume) / fade_in_time
                        
                        self.current_music = 'game'
                        music_loaded = True
                        debug_print(f"🎵 Game music loaded and started: {music_file}")
                        debug_print(f"🎵 Fading from {start_volume} to {self.game_music_volume} over {fade_in_time}s")
                        break
                    else:
                        debug_print(f"⚠️ Music loaded but failed to start: {music_file}")
                        
                except pygame.error as e:
                    debug_print(f"❌ Error loading game music {music_file}: {e}")
                    continue
        
        if not music_loaded:
            debug_print("❌ CRITICAL: No game music files found or failed to load")
            self.current_music = None
    
    def fade_out_music(self, fade_time: float = 1.5):
        """Fade out current music."""
        if not self.audio_enabled or not pygame.mixer.music.get_busy():
            return
        
        current_volume = pygame.mixer.music.get_volume()
        self.is_fading = True
        self.fade_target_volume = 0.0
        self.fade_speed = current_volume / fade_time
        debug_print(f"🎵 Fading out music over {fade_time} seconds")
    
    def update_music_fade(self, dt: float):
        """Update music fading - IMPROVED stability."""
        if not self.is_fading or not self.audio_enabled:
            return
        
        # Handle both milliseconds and seconds
        dt_sec = dt * 0.001 if dt > 1 else dt
        
        # CRITICAL: Safety check - ensure music is still playing
        if not pygame.mixer.music.get_busy():
            if self.fade_target_volume > 0:
                debug_print("⚠️ Music stopped during fade, attempting restart...")
                # Try to restart the music
                if self.current_music == 'game':
                    self.play_game_music(1.0)  # Quick restart
                return
            else:
                # Fade out completed normally
                self.is_fading = False
                self.current_music = None
                debug_print("🎵 Music fade-out completed normally")
                return
        
        current_volume = pygame.mixer.music.get_volume()
        
        # Calculate volume change
        if self.fade_target_volume > current_volume:
            # Fading in
            new_volume = min(self.fade_target_volume, 
                           current_volume + self.fade_speed * dt_sec)
        else:
            # Fading out
            new_volume = max(self.fade_target_volume, 
                           current_volume - self.fade_speed * dt_sec)
        
        # Apply new volume
        pygame.mixer.music.set_volume(new_volume)
        
        # Check if fade is complete
        if abs(new_volume - self.fade_target_volume) < 0.01:
            self.is_fading = False
            pygame.mixer.music.set_volume(self.fade_target_volume)  # Set exact target
            
            if self.fade_target_volume == 0.0:
                pygame.mixer.music.stop()
                self.current_music = None
                debug_print("🎵 Music fade-out completed")
            else:
                debug_print(f"🎵 Music fade-in completed at volume {self.fade_target_volume}")
    
    def crossfade_to_game_music(self, fade_time: float = 2.0):
        """Smoothly transition from menu to game music."""
        if self.current_music == 'game':
            debug_print("🎵 Game music already playing, skipping crossfade")
            return  # Already playing game music
        
        debug_print(f"🎵 Starting crossfade from {self.current_music} to game music...")
        
        # CRITICAL: Stop all existing timers first to prevent conflicts
        pygame.time.set_timer(pygame.USEREVENT + 2, 0)
        pygame.time.set_timer(pygame.USEREVENT + 3, 0)
        pygame.time.set_timer(pygame.USEREVENT + 4, 0)
        pygame.time.set_timer(pygame.USEREVENT + 5, 0)
        
        # Stop current music immediately
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            debug_print("🎵 Stopped current music immediately")
        
        # Clear fading state
        self.is_fading = False
        self.current_music = None
        
        # Start game music immediately with fade-in
        self.play_game_music(fade_time)
    
    def handle_crossfade_event(self, event):
        """Handle crossfade timing events."""
        if event.type == pygame.USEREVENT + 2:
            # Start game music with fade-in
            self.play_game_music(1.5)  # Fade in over 1.5 seconds
            pygame.time.set_timer(pygame.USEREVENT + 2, 0)  # Cancel timer
    
    def return_to_menu_music(self, fade_time: float = 1.0):
        """Return to menu music from game."""
        debug_print("🎵 Returning to menu music...")
        
        # Fade out current music
        if pygame.mixer.music.get_busy() and self.current_music == 'game':
            self.fade_out_music(fade_time)
            
            # Set timer to start menu music after fade out
            pygame.time.set_timer(pygame.USEREVENT + 3, int(fade_time * 1000 + 200))
        else:
            # Start menu music immediately if no game music playing
            self.play_menu_music()
    
    def handle_menu_return_event(self, event):
        """Handle menu return timing events."""
        if event.type == pygame.USEREVENT + 3:
            # Start menu music
            self.play_menu_music()
            pygame.time.set_timer(pygame.USEREVENT + 3, 0)  # Cancel timer
    
    def play_music(self, music_file: str, loop: bool = True):
        """Play background music."""
        if not self.audio_enabled:
            return
        
        music_path = os.path.join("assets/sounds", music_file)
        
        if os.path.exists(music_path):
            try:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.play(-1 if loop else 0)
                debug_print(f"🎵 Playing music: {music_file}")
            except pygame.error as e:
                debug_print(f"❌ Error playing music {music_file}: {e}")
        else:
            debug_print(f"⚠️ Music file not found: {music_path}")

    def stop_music(self):
        """Stop background music."""
        if self.audio_enabled:
            pygame.mixer.music.stop()
            self.current_music = None
    
    def set_sound_volume(self, volume: float):
        """Set sound effects volume (0.0 to 1.0)."""
        self.sound_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            if sound is not None:
                sound.set_volume(self.sound_volume)
    
    def set_music_volume(self, volume: float):
        """Set music volume (0.0 to 1.0) and update current music."""
        self.music_volume = max(0.0, min(1.0, volume))
        self.menu_music_volume = self.music_volume * 1.25  # Menu slightly louder
        self.game_music_volume = self.music_volume * 0.6   # Game much quieter
        
        if self.audio_enabled and pygame.mixer.music.get_busy():
            if self.current_music == 'menu':
                pygame.mixer.music.set_volume(self.menu_music_volume)
            elif self.current_music == 'game':
                pygame.mixer.music.set_volume(self.game_music_volume)

    def cleanup(self):
        """Clean up audio resources."""
        if self.audio_enabled:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
            debug_print("🧹 Audio cleanup complete")