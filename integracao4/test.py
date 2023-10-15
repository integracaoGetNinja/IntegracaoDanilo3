import os
import time

def limpar_terminal():
    if os.name == 'nt':  # Verifica se o sistema operacional é Windows
        os.system('cls')  # Limpa o terminal no Windows
    else:
        os.system('clear')  # Limpa o terminal em sistemas tipo Unix (macOS, Linux)

print("fijasdjasjdia")
time.sleep(1)
print("fijasdjasjdia")
time.sleep(1)

# Limpar o terminal usando a função personalizada
limpar_terminal()

print("aushuadhsu")
