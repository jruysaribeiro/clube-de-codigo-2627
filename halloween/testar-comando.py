# =====================================================================
# TESTAR O COMANDO
# Liga o comando (cabo ou Bluetooth), corre isto, e mexe em tudo.
# Mostra no ecra o que o computador esta a receber do comando.
# Se aqui nao aparecer nada, o jogo tambem nao o vai ver.
# =====================================================================

import pygame

pygame.init()
ecra = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Testar o comando")
clock = pygame.time.Clock()
fonte = pygame.font.SysFont(None, 28)

comandos = []
a_correr = True
while a_correr:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            a_correr = False
        if evento.type == pygame.JOYDEVICEADDED:
            comandos.append(pygame.joystick.Joystick(evento.device_index))
        if evento.type == pygame.JOYDEVICEREMOVED:
            ficam = []
            for comando in comandos:
                if comando.get_instance_id() != evento.instance_id:
                    ficam.append(comando)
            comandos = ficam
        if evento.type == pygame.JOYBUTTONDOWN:
            # Carregar num botao faz o comando tremer: assim sabes que vibra.
            for comando in comandos:
                comando.rumble(0.6, 0.6, 200)

    ecra.fill((20, 20, 30))
    y = 20
    if len(comandos) == 0:
        ecra.blit(fonte.render("Nenhum comando ligado. Liga-o agora.", True, (240, 200, 70)), (20, y))
    for comando in comandos:
        ecra.blit(fonte.render(comando.get_name(), True, (240, 200, 70)), (20, y))
        y = y + 34
        eixos = "Eixos: "
        indice = 0
        while indice < comando.get_numaxes():
            eixos = eixos + str(indice) + "=" + str(round(comando.get_axis(indice), 2)) + "  "
            indice = indice + 1
        ecra.blit(fonte.render(eixos, True, (240, 240, 240)), (20, y))
        y = y + 34
        botoes = "Botoes carregados: "
        indice = 0
        while indice < comando.get_numbuttons():
            if comando.get_button(indice):
                botoes = botoes + str(indice) + " "
            indice = indice + 1
        ecra.blit(fonte.render(botoes, True, (240, 240, 240)), (20, y))
        y = y + 34
        if comando.get_numhats() > 0:
            ecra.blit(fonte.render("Setas (hat): " + str(comando.get_hat(0)), True, (240, 240, 240)), (20, y))
            y = y + 34
        y = y + 20
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
