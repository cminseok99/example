import pygame
import os
import sys
import logging

# 기본 초기화(반드시 해야 하는 것들)
pygame.init()

# 배경음악
test_sound = pygame.mixer.Sound("C:\\Users\\차민석\\Desktop\\pythonworkspace\\pygame_project\\images\\22359B485825FA0306.mp3")
test_sound.play(-1)

# 화면 크기 설정
screen_width = 640
screen_height = 480
screen = pygame.display.set_mode((screen_width, screen_height))  # 반드시 해야하는 것들

# 화면 타이틀 설정
pygame.display.set_caption("nado pang")

# FPS
clock = pygame.time.Clock()

###################################################################

# 사용자 게임 초기화 (배경 화면, 게임 이미지, 좌표, 속도, 폰트 등)
current_path = os.path.dirname(__file__)  # 현재 파일의 위치 반환
image_path = os.path.join(current_path, "images")  # images 폴더 위치 반환

# 배경 만들기
background = pygame.image.load(os.path.join(image_path, "background.png"))

# 스테이지 만들기
stage = pygame.image.load(os.path.join(image_path, "stage.png"))
stage_size = stage.get_rect().size
stage_height = stage_size[1]  # 스테이지 높이 위에 캐릭터를 두기 위해 사용

# 캐릭터 만들기
character = pygame.image.load(os.path.join(image_path, "character.png"))
character.set_colorkey((255, 255, 255))
character_size = character.get_rect().size
character_width = character_size[0]
character_height = character_size[1]
character_x_pos = (screen_width / 2) - (character_width / 2)
character_y_pos = screen_height - character_height - stage_height

# 캐릭터 이동 방향
character_to_x = 0

# 캐릭터 이동 속도
character_speed = 10

# 무기 만들기
weapon = pygame.image.load(os.path.join(image_path, "weapon.png"))
weapon.set_colorkey((255, 255, 255))
weapon_size = weapon.get_rect().size
weapon_width = weapon_size[0]
weapon_height = weapon_size[1]

# 무기 제한 관련 변수
max_shots = 100  # 최대 발사 횟수
shot_count = 0  # 현재까지 발사한 횟수
last_shot_time = 0  # 마지막으로 무기를 발사한 시간
weapon_cooldown = 500  # 무기 발사 간격 (ms) 2초에 1번씩

# 무기는 한 번에 여러 발 발사 가능
weapons = []

# 무기 이동 속도
weapon_speed = 15

# 공 만들기 (4개 크기에 대해 따로 처리)
ball_images = [
    pygame.image.load(os.path.join(image_path, "balloon1.png")),
    pygame.image.load(os.path.join(image_path, "balloon2.png")),
    pygame.image.load(os.path.join(image_path, "balloon3.png")),
    pygame.image.load(os.path.join(image_path, "balloon4.png")),
    pygame.image.load(os.path.join(image_path, "balloon5.png")),
]

# 공 위치 정하기
ball_x_pos = (screen_width / 2) - (100 / 2)
ball_y_pos = screen_height - stage_height

for image in ball_images:
    image.set_colorkey((255, 255, 255))

# 공 크기에 따른 최초 스피드
ball_speed_y = [-10, -7, -5, -3, -1]  # index 0,1,2,3 에 해당하는 값

# 공들
balls = []

# 최초 발생하는 큰 공 추가
balls.append({
    "pos_x": 50,  # 공의 x 좌표
    "pos_y": 50,  # 공의 y 좌표
    "img_idx": 0,  # 공의 이미지 인덱스
    "to_x": 3,  # x축 이동방향 -3이면 왼쪽으로 , 3이면 오른쪽으로
    "to_y": -6,  # y축 이동방향,
    "init_spd_y": ball_speed_y[0]})  # y 최초 속도

# 사라질 무기, 공 정보 저장 변수
weapon_to_remove = -1
ball_to_remove = -1

# font 정의
game_font = pygame.font.Font(None, 40)
total_time = 65
start_ticks = pygame.time.get_ticks()  # 시작 시간 정의

# score 정의
score = 0

# 게임 종료 메시지 / timeout(시간 초과),mission complete(성공),game over(캐릭터 죽음)
game_result = "Game over"
running = True

# 시작화면 이미지
start_img = pygame.image.load(os.path.join(image_path, "start_img.png"))
exit_img = pygame.image.load(os.path.join(image_path, "exit_img.png"))

# 현재 스테이지 레벨
stage_level = 1

class MainMenu:
    def __init__(self):
        self.start_button = Button(100, 200, start_img, 0.8)
        self.exit_button = Button(450, 200, exit_img, 0.8)

    def show(self):
        run = True
        while run:
            screen.fill((202, 228, 241))

            if self.start_button.draw(screen):
                return "start"
            if self.exit_button.draw(screen):
                pygame.quit()
                sys.exit()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.display.update()

class Button:
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self, surface):
        action = False
        # get mouse position
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        surface.blit(self.image, (self.rect.x, self.rect.y))

        return action

def next_stage():
    global stage_level
    stage_level += 1  # 다음 스테이지 레벨로 업데이트
    initialize_stage()

def initialize_stage():
    global balls, weapons
    balls = []
    weapons = []
    create_ball()

def create_ball():
    delay = 1200
    pygame.time.set_timer(delay, 1000)
    if len(balls) == 0:
        ball_x_pos = (screen_width / 2) - (100 / 2)
        ball_y_pos = screen_height - stage_height
        balls.append({
            "pos_x": ball_x_pos,  # 공의 x 좌표
            "pos_y": ball_y_pos,  # 공의 y 좌표
            "img_idx": 0,  # 공의 이미지 인덱스
            "to_x": 3,  # x축 이동방향 -3이면 왼쪽으로 , 3이면 오른쪽으로
            "to_y": -6,  # y축 이동방향,
            "init_spd_y": ball_speed_y[0]})  # y 최초 속도

# 이벤트 루프
main_menu = MainMenu()
game_result = main_menu.show()
start_button_rect = start_img.get_rect(topleft=(100, 200))

while running:
    dt = clock.tick(15)  # 게임화면의 초당 프레임 수를 설정

    if game_result == "start":
        for event in pygame.event.get():  # 이벤트 처리
            if event.type == pygame.QUIT:  # 창이 닫히는 이벤트가 발생하였는가?
                running = False  # 게임이 진행중이 아님
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:  # 캐릭터를 왼쪽으로
                    character_to_x -= character_speed
                elif event.key == pygame.K_RIGHT:  # 캐릭터를 오른쪽으로
                    character_to_x += character_speed
                elif event.key == pygame.K_SPACE:  # 무기 발사
                    if shot_count < max_shots and pygame.time.get_ticks() - last_shot_time >= weapon_cooldown:
                        weapons.append([character_x_pos + (character_width / 2) - (weapon_width / 2),
                                        character_y_pos - weapon_height])
                        last_shot_time = pygame.time.get_ticks()
                        shot_count += 1

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    character_to_x = 0

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                # 클릭한 좌표에 해당하는 버튼 확인 후 해당 버튼 기능 수행
                if pos[0] > screen_width / 2 - start_button_rect.width / 2 and \
                        pos[0] < screen_width / 2 - start_button_rect.width / 2 + start_button_rect.width:
                    if pos[1] > 200 and pos[1] < 200 + start_button_rect.height:
                        game_result = "start"

    # 여기서 게임 상태에 따른 렌더링 및 업데이트 작업을 수행해야 합니다.




    

        character_x_pos += character_to_x

        # 캐릭터의 위치를 화면 경계 내에서만 이동
        if character_x_pos < 0:
            character_x_pos = 0
        elif character_x_pos > screen_width - character_width:
            character_x_pos = screen_width - character_width

        # 무기 위치 조정
        weapons = [[w[0], w[1] - weapon_speed] for w in weapons]

        # 천장에 닿은 무기 없애기
        weapons = [[w[0], w[1]] for w in weapons if w[1] > 0]

        # 공 위치 정의
        for ball_idx, ball_val in enumerate(balls):
            ball_pos_x = ball_val["pos_x"]
            ball_pos_y = ball_val["pos_y"]
            ball_img_idx = ball_val["img_idx"]

            ball_size = ball_images[ball_img_idx].get_rect().size
            ball_width = ball_size[0]
            ball_height = ball_size[1]

            # 가로 경계 설정
            if ball_pos_x <= 0 or ball_pos_x >= screen_width - ball_width:
                ball_val["to_x"] = ball_val["to_x"] * -1

            # 세로 위치
            if ball_pos_y >= screen_height - stage_height - ball_height:
                ball_val["to_y"] = ball_val["init_spd_y"]
            else:
                ball_val["to_y"] += 0.5

            ball_val["pos_x"] += ball_val["to_x"]
            ball_val["pos_y"] += ball_val["to_y"]

        # 캐릭터 rect 정보 업데이트
        character_rect = character.get_rect()
        character_rect.left = character_x_pos
        character_rect.top = character_y_pos

        # 충돌 체크
        for ball_idx, ball_val in enumerate(balls):
            ball_pos_x = ball_val["pos_x"]
            ball_pos_y = ball_val["pos_y"]
            ball_img_idx = ball_val["img_idx"]

            ball_rect = ball_images[ball_img_idx].get_rect()
            ball_rect.left = ball_pos_x
            ball_rect.top = ball_pos_y

            # 공과 캐릭터 충돌 처리
            if character_rect.colliderect(ball_rect):
                running = False
                break

            # 공과 무기들 충돌 처리
            for weapon_idx, weapon_val in enumerate(weapons):
                weapon_pos_x = weapon_val[0]
                weapon_pos_y = weapon_val[1]

                weapon_rect = weapon.get_rect()
                weapon_rect.left = weapon_pos_x
                weapon_rect.top = weapon_pos_y

                # 충돌 체크
                if weapon_rect.colliderect(ball_rect):
                    weapon_to_remove = weapon_idx
                    ball_to_remove = ball_idx

                    # 가장 작은 크기의 공이 아니라면 다음 단계의 공으로 나눠주기
                    if ball_img_idx < 4:
                        # 현재 공 크기 정보를 가지고 옴
                        ball_width = ball_rect.size[0]
                        ball_height = ball_rect.size[1]

                        # 나눠진 공 정보
                        small_ball_rect = ball_images[ball_img_idx + 1].get_rect()
                        small_ball_width = small_ball_rect.size[0]
                        small_ball_height = small_ball_rect.size[1]

                        # 왼쪽으로 튕겨나가는 작은 공
                        balls.append({
                            "pos_x": ball_pos_x + (ball_width / 2) - (small_ball_width / 2),  # 공의 x 좌표
                            "pos_y": ball_pos_y + (ball_height / 2) - (small_ball_height / 2),  # 공의 y 좌표
                            "img_idx": ball_img_idx + 1,  # 공의 이미지 인덱스
                            "to_x": -3,  # x축 이동방향 -3이면 왼쪽으로 , 3이면 오른쪽으로
                            "to_y": -6,  # y축 이동방향,
                            "init_spd_y": ball_speed_y[ball_img_idx + 1]})  # y 최초 속도

                        # 오른쪽으로 튕겨나가는 작은 공
                        balls.append({
                            "pos_x": ball_pos_x + (ball_width / 2) - (small_ball_width / 2),  # 공의 x 좌표
                            "pos_y": ball_pos_y + (ball_height / 2) - (small_ball_height / 2),  # 공의 y 좌표
                            "img_idx": ball_img_idx + 1,  # 공의 이미지 인덱스
                            "to_x": 3,  # x축 이동방향 -3이면 왼쪽으로 , 3이면 오른쪽으로
                            "to_y": -6,  # y축 이동방향,
                            "init_spd_y": ball_speed_y[ball_img_idx + 1]})  # y 최초 속도

                    break
            else:
                continue
            break

        # 충돌된 공 or 무기 없애기
        if ball_to_remove > -1:
            del balls[ball_to_remove]
            ball_to_remove = -1

        if weapon_to_remove > -1:
            del weapons[weapon_to_remove]
            weapon_to_remove = -1

        # 모든 공을 없앤 경우 게임 종료 (성공)
        if len(balls) == 0:
            game_result = "Mission Complete"
            running = False

        # 화면에 그리기
        screen.blit(background, (0, 0))
        for weapon_x_pos, weapon_y_pos in weapons:
            screen.blit(weapon, (weapon_x_pos, weapon_y_pos))

        for idx, val in enumerate(balls):
            ball_pos_x = val["pos_x"]
            ball_pos_y = val["pos_y"]
            ball_img_idx = val["img_idx"]
            screen.blit(ball_images[ball_img_idx], (ball_pos_x, ball_pos_y))

        screen.blit(stage, (0, screen_height - stage_height))
        screen.blit(character, (character_x_pos, character_y_pos))

        # 경과 시간 계산
        elapsed_time = (pygame.time.get_ticks() - start_ticks) / 1000
        timer = game_font.render("Time : {}".format(int(total_time - elapsed_time)), True, (255, 255, 255))
        screen.blit(timer, (10, 10))

        # 시간 초과했다면
        if total_time - elapsed_time <= 0:
            game_result = "Time Over"
            running = False

        pygame.display.update()  # 게임화면을 다시 그리기!

# 게임 오버 메시지
msg = game_font.render(game_result, True, (255, 255, 0))  # 노란색
msg_rect = msg.get_rect(center=(int(screen_width / 2), int(screen_height / 2)))
screen.blit(msg, msg_rect)
pygame.display.update()
pygame.time.delay(2000)

pygame.quit()
