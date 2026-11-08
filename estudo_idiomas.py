"""
Módulo de Estudo Lúdico de Idiomas (Inglês e Espanhol) — Jarvis Kids OS
Projetado especialmente para Kaleo Noah (~4 anos).
Foco pedagógico:
1. Imersão visual e sonora com cards táteis e grandes.
2. Vocabulário essencial do cotidiano infantil: Animais, Cores, Mãozinhas & Números, Comidas, Saudações, Família.
3. Pronúncia fonética aproximada e áudio interativo.
4. Mini-quiz "Adivinhe a Palavra / Onde Está?" com reforço positivo imediato e moedas no Pote do Tesouro.
5. Integração com SQLite WAL para persistência leve de progresso.
"""

import random
from typing import Dict, List, Optional, Tuple
import banco_dados
from economia_fichas import token_mgr


# ==============================================================================
# DICIONÁRIO ESTRUTURADO DE VOCABULÁRIO INFANTIL
# ==============================================================================

CATEGORIAS = [
    {
        "id": "animais",
        "nome": "Animais Amigos",
        "nome_en": "Animal Friends",
        "nome_es": "Amigos Animales",
        "icone": "🐶",
        "cor": "#10b981",
        "descricao": "Bichinhos fofos da fazenda, floresta e safari!",
    },
    {
        "id": "cores",
        "nome": "Cores Mágicas",
        "nome_en": "Magic Colors",
        "nome_es": "Colores Mágicos",
        "icone": "🎨",
        "cor": "#f59e0b",
        "descricao": "Todas as cores do arco-íris para pintar o mundo!",
    },
    {
        "id": "numeros",
        "nome": "Mãozinhas & Números",
        "nome_en": "Fingers & Numbers",
        "nome_es": "Manitas y Números",
        "icone": "🖐️",
        "cor": "#0284c7",
        "descricao": "Contando de 1 a 10 usando os dedinhos das mãos!",
    },
    {
        "id": "comidas",
        "nome": "Frutinhas & Comidinhas",
        "nome_en": "Fruits & Food",
        "nome_es": "Frutas y Comida",
        "icone": "🍎",
        "cor": "#ef4444",
        "descricao": "Alimentos saudáveis e gostosos que dão superpoderes!",
    },
    {
        "id": "saudacoes",
        "nome": "Saudações & Carinho",
        "nome_en": "Greetings & Love",
        "nome_es": "Saludos y Amor",
        "icone": "👋",
        "cor": "#8b5cf6",
        "descricao": "Palavrinhas mágicas para falar com todo mundo!",
    },
    {
        "id": "familia",
        "nome": "Família do Coração",
        "nome_en": "Loving Family",
        "nome_es": "Familia Querida",
        "icone": "👨‍👩‍👦",
        "cor": "#ec4899",
        "descricao": "Papai, mamãe, irmãos e os melhores amigos!",
    },
]

VOCABULARIO = [
    # --- ANIMAIS ---
    {
        "id": "dog",
        "categoria": "animais",
        "pt": "Cachorro",
        "en": "Dog",
        "en_som": "Dóg",
        "es": "Perro",
        "es_som": "Pê-rro",
        "icone": "🐶",
        "som_animal": "Au au! / Woof woof!",
        "gesto": "Faça carinho na orelhinha!",
    },
    {
        "id": "cat",
        "categoria": "animais",
        "pt": "Gato",
        "en": "Cat",
        "en_som": "Két",
        "es": "Gato",
        "es_som": "Gá-to",
        "icone": "🐱",
        "som_animal": "Miau! / Meow!",
        "gesto": "Passe a mãozinha como um gatinho!",
    },
    {
        "id": "lion",
        "categoria": "animais",
        "pt": "Leão",
        "en": "Lion",
        "en_som": "Lái-on",
        "es": "León",
        "es_som": "Le-ón",
        "icone": "🦁",
        "som_animal": "Rooaaar!",
        "gesto": "Mostre as garrinhas de herói!",
    },
    {
        "id": "duck",
        "categoria": "animais",
        "pt": "Pato",
        "en": "Duck",
        "en_som": "Dâk",
        "es": "Pato",
        "es_som": "Pá-to",
        "icone": "🦆",
        "som_animal": "Quack quack!",
        "gesto": "Bata as asinhas como um patinho!",
    },
    {
        "id": "bird",
        "categoria": "animais",
        "pt": "Pássaro",
        "en": "Bird",
        "en_som": "Bêrd",
        "es": "Pájaro",
        "es_som": "Pá-rra-ro",
        "icone": "🐦",
        "som_animal": "Piu piu! / Tweet tweet!",
        "gesto": "Voe bem alto com os bracinhos!",
    },
    {
        "id": "fish",
        "categoria": "animais",
        "pt": "Peixe",
        "en": "Fish",
        "en_som": "Fíxi",
        "es": "Pez",
        "es_som": "Pês",
        "icone": "🐟",
        "som_animal": "Glub glub!",
        "gesto": "Junte as duas mãozinhas nadando!",
    },
    {
        "id": "elephant",
        "categoria": "animais",
        "pt": "Elefante",
        "en": "Elephant",
        "en_som": "É-le-fant",
        "es": "Elefante",
        "es_som": "E-le-fán-te",
        "icone": "🐘",
        "som_animal": "Fruuuum!",
        "gesto": "Faça uma tromba com o braço!",
    },
    {
        "id": "monkey",
        "categoria": "animais",
        "pt": "Macaco",
        "en": "Monkey",
        "en_som": "Mân-ki",
        "es": "Mono",
        "es_som": "Mó-no",
        "icone": "🐵",
        "som_animal": "U-u-a-a!",
        "gesto": "Pule alegremente como o macaquinho!",
    },

        {
        "id": "horse",
        "categoria": "animais",
        "pt": "Cavalo",
        "en": "Horse",
        "en_som": "Rórs",
        "es": "Caballo",
        "es_som": "Ka-bá-lo",
        "icone": "🐴",
        "som_animal": "Iiiirrrrí!",
        "gesto": "Galope com as mãozinhas!",
    },
    {
        "id": "cow",
        "categoria": "animais",
        "pt": "Vaca",
        "en": "Cow",
        "en_som": "Cáu",
        "es": "Vaca",
        "es_som": "Vá-ka",
        "icone": "🐮",
        "som_animal": "Muuuu!",
        "gesto": "Dá leite quentinho e gostoso!",
    },
    {
        "id": "bear",
        "categoria": "animais",
        "pt": "Urso",
        "en": "Bear",
        "en_som": "Bér",
        "es": "Oso",
        "es_som": "Ó-so",
        "icone": "🐻",
        "som_animal": "Grrr-roar!",
        "gesto": "Dê um abraço de urso bem apertado!",
    },
    {
        "id": "rabbit",
        "categoria": "animais",
        "pt": "Coelho",
        "en": "Rabbit",
        "en_som": "Ré-bit",
        "es": "Conejo",
        "es_som": "Ko-né-rro",
        "icone": "🐰",
        "som_animal": "Pula-pula!",
        "gesto": "Mexa o narizinho como um coelho!",
    },
    # --- CORES ---
    {
        "id": "red",
        "categoria": "cores",
        "pt": "Vermelho",
        "en": "Red",
        "en_som": "Réd",
        "es": "Rojo",
        "es_som": "Ró-rro",
        "icone": "🔴",
        "cor_hex": "#ef4444",
        "gesto": "Cor do morango e do coração!",
    },
    {
        "id": "blue",
        "categoria": "cores",
        "pt": "Azul",
        "en": "Blue",
        "en_som": "Blu",
        "es": "Azul",
        "es_som": "A-súl",
        "icone": "🔵",
        "cor_hex": "#3b82f6",
        "gesto": "Cor do céu e do marzão!",
    },
    {
        "id": "yellow",
        "categoria": "cores",
        "pt": "Amarelo",
        "en": "Yellow",
        "en_som": "Ié-lou",
        "es": "Amarillo",
        "es_som": "A-ma-rí-lo",
        "icone": "🟡",
        "cor_hex": "#eab308",
        "gesto": "Cor do sol quentinho e da banana!",
    },
    {
        "id": "green",
        "categoria": "cores",
        "pt": "Verde",
        "en": "Green",
        "en_som": "Grin",
        "es": "Verde",
        "es_som": "Vér-de",
        "icone": "🟢",
        "cor_hex": "#22c55e",
        "gesto": "Cor das plantinhas e do Hulk!",
    },
    {
        "id": "orange",
        "categoria": "cores",
        "pt": "Laranja",
        "en": "Orange",
        "en_som": "Ó-rindj",
        "es": "Naranja",
        "es_som": "Na-rán-rra",
        "icone": "🟠",
        "cor_hex": "#f97316",
        "gesto": "Cor da cenoura crocante!",
    },
    {
        "id": "pink",
        "categoria": "cores",
        "pt": "Rosa",
        "en": "Pink",
        "en_som": "Pinc",
        "es": "Rosa",
        "es_som": "Ró-sa",
        "icone": "🌸",
        "cor_hex": "#ec4899",
        "gesto": "Cor da florzinha cheirosa!",
    },
    {
        "id": "purple",
        "categoria": "cores",
        "pt": "Roxo",
        "en": "Purple",
        "en_som": "Pêr-pol",
        "es": "Morado",
        "es_som": "Mo-rá-do",
        "icone": "🟣",
        "cor_hex": "#a855f7",
        "gesto": "Cor da uva docinha!",
    },
    {
        "id": "white",
        "categoria": "cores",
        "pt": "Branco",
        "en": "White",
        "en_som": "Uáit",
        "es": "Blanco",
        "es_som": "Blán-ko",
        "icone": "⚪",
        "cor_hex": "#ffffff",
        "gesto": "Cor das nuvens fofinhas!",
    },

        {
        "id": "black",
        "categoria": "cores",
        "pt": "Preto",
        "en": "Black",
        "en_som": "Bléc",
        "es": "Negro",
        "es_som": "Né-gro",
        "icone": "🖤",
        "cor_hex": "#0f172a",
        "gesto": "Cor da noite estrelada e do espaço!",
    },
    {
        "id": "brown",
        "categoria": "cores",
        "pt": "Marrom",
        "en": "Brown",
        "en_som": "Bráun",
        "es": "Marrón",
        "es_som": "Ma-rrón",
        "icone": "🟤",
        "cor_hex": "#78350f",
        "gesto": "Cor do chocolate docinho e da terra!",
    },
    {
        "id": "gray",
        "categoria": "cores",
        "pt": "Cinza",
        "en": "Gray",
        "en_som": "Grêi",
        "es": "Gris",
        "es_som": "Gris",
        "icone": "🩶",
        "cor_hex": "#64748b",
        "gesto": "Cor da armadura de ferro do Stark!",
    },
    {
        "id": "rainbow",
        "categoria": "cores",
        "pt": "Arco-Íris",
        "en": "Rainbow",
        "en_som": "Rêin-bou",
        "es": "Arcoíris",
        "es_som": "Ar-ko-í-ris",
        "icone": "🌈",
        "cor_hex": "#ec4899",
        "gesto": "Todas as cores juntas brilhando no céu!",
    },
    # --- MÃOZINHAS E NÚMEROS (ENSINANDO A CONTAR COM OS DEDOS) ---
    {
        "id": "num_1",
        "categoria": "numeros",
        "pt": "1 (Um)",
        "en": "One",
        "en_som": "Uan",
        "es": "Uno",
        "es_som": "Ú-no",
        "icone": "☝️",
        "numero": 1,
        "gesto": "1 dedinho para o alto!",
    },
    {
        "id": "num_2",
        "categoria": "numeros",
        "pt": "2 (Dois)",
        "en": "Two",
        "en_som": "Tu",
        "es": "Dos",
        "es_som": "Dós",
        "icone": "✌️",
        "numero": 2,
        "gesto": "2 dedinhos: sinal da paz!",
    },
    {
        "id": "num_3",
        "categoria": "numeros",
        "pt": "3 (Três)",
        "en": "Three",
        "en_som": "Trí",
        "es": "Tres",
        "es_som": "Trés",
        "icone": "🤟",
        "numero": 3,
        "gesto": "3 dedinhos levantados!",
    },
    {
        "id": "num_4",
        "categoria": "numeros",
        "pt": "4 (Quatro)",
        "en": "Four",
        "en_som": "Fór",
        "es": "Cuatro",
        "es_som": "Kuá-tro",
        "icone": "🖖",
        "numero": 4,
        "gesto": "4 dedinhos abertos!",
    },
    {
        "id": "num_5",
        "categoria": "numeros",
        "pt": "5 (Cinco)",
        "en": "Five",
        "en_som": "Fáiv",
        "es": "Cinco",
        "es_som": "Sín-ko",
        "icone": "🖐️",
        "numero": 5,
        "gesto": "Mãozinha aberta com 5!",
    },
    {
        "id": "num_6",
        "categoria": "numeros",
        "pt": "6 (Seis)",
        "en": "Six",
        "en_som": "Sícs",
        "es": "Seis",
        "es_som": "Séis",
        "icone": "✋☝️",
        "numero": 6,
        "gesto": "5 numa mão + 1 dedinho!",
    },
    {
        "id": "num_7",
        "categoria": "numeros",
        "pt": "7 (Sete)",
        "en": "Seven",
        "en_som": "Sé-ven",
        "es": "Siete",
        "es_som": "Sié-te",
        "icone": "✋✌️",
        "numero": 7,
        "gesto": "5 numa mão + 2 dedinhos!",
    },
    {
        "id": "num_8",
        "categoria": "numeros",
        "pt": "8 (Oito)",
        "en": "Eight",
        "en_som": "Éit",
        "es": "Ocho",
        "es_som": "Ó-tcho",
        "icone": "✋🤟",
        "numero": 8,
        "gesto": "5 numa mão + 3 dedinhos!",
    },
    {
        "id": "num_9",
        "categoria": "numeros",
        "pt": "9 (Nove)",
        "en": "Nine",
        "en_som": "Náin",
        "es": "Nueve",
        "es_som": "Nué-ve",
        "icone": "✋🖖",
        "numero": 9,
        "gesto": "5 numa mão + 4 dedinhos!",
    },
    {
        "id": "num_10",
        "categoria": "numeros",
        "pt": "10 (Dez)",
        "en": "Ten",
        "en_som": "Tén",
        "es": "Diez",
        "es_som": "Di-és",
        "icone": "👐",
        "numero": 10,
        "gesto": "As duas mãos abertas: 10!",
    },

        {
        "id": "num_0",
        "categoria": "numeros",
        "pt": "0 (Zero)",
        "en": "Zero",
        "en_som": "Zí-rou",
        "es": "Cero",
        "es_som": "Sé-ro",
        "icone": "0️⃣",
        "numero": 0,
        "gesto": "Mãozinha fechada: zero!",
    },
    {
        "id": "num_20",
        "categoria": "numeros",
        "pt": "20 (Vinte)",
        "en": "Twenty",
        "en_som": "Tu-én-ti",
        "es": "Veinte",
        "es_som": "Béin-te",
        "icone": "🔟🔟",
        "numero": 20,
        "gesto": "Bata duas palminhas de 10!",
    },
    # --- COMIDAS E FRUTINHAS ---
    {
        "id": "apple",
        "categoria": "comidas",
        "pt": "Maçã",
        "en": "Apple",
        "en_som": "É-pol",
        "es": "Manzana",
        "es_som": "Man-sá-na",
        "icone": "🍎",
        "gesto": "Faça o som de morder uma maçã: Nhac!",
    },
    {
        "id": "banana",
        "categoria": "comidas",
        "pt": "Banana",
        "en": "Banana",
        "en_som": "Ba-né-na",
        "es": "Plátano",
        "es_som": "Plá-ta-no",
        "icone": "🍌",
        "gesto": "Finja descascar uma banana!",
    },
    {
        "id": "water",
        "categoria": "comidas",
        "pt": "Água",
        "en": "Water",
        "en_som": "Uó-ter",
        "es": "Agua",
        "es_som": "Á-gua",
        "icone": "💧",
        "gesto": "Beba água para recarregar as energias!",
    },
    {
        "id": "milk",
        "categoria": "comidas",
        "pt": "Leite",
        "en": "Milk",
        "en_som": "Mílc",
        "es": "Leche",
        "es_som": "Lé-tche",
        "icone": "🥛",
        "gesto": "Leitinho quentinho fortalece os ossos!",
    },
    {
        "id": "bread",
        "categoria": "comidas",
        "pt": "Pão",
        "en": "Bread",
        "en_som": "Bréd",
        "es": "Pan",
        "es_som": "Pán",
        "icone": "🍞",
        "gesto": "Pãozinho quentinho no café da manhã!",
    },
    {
        "id": "cookie",
        "categoria": "comidas",
        "pt": "Biscoito",
        "en": "Cookie",
        "en_som": "Cú-ki",
        "es": "Galleta",
        "es_som": "Ga-lié-ta",
        "icone": "🍪",
        "gesto": "Biscoitinho crocante!",
    },

        {
        "id": "strawberry",
        "categoria": "comidas",
        "pt": "Morango",
        "en": "Strawberry",
        "en_som": "Stró-bé-ri",
        "es": "Fresa",
        "es_som": "Fré-sa",
        "icone": "🍓",
        "gesto": "Frutinha vermelha docinha!",
    },
    {
        "id": "grape",
        "categoria": "comidas",
        "pt": "Uva",
        "en": "Grapes",
        "en_som": "Gréips",
        "es": "Uvas",
        "es_som": "Ú-vas",
        "icone": "🍇",
        "gesto": "Cachinho roxo delicioso!",
    },
    {
        "id": "watermelon",
        "categoria": "comidas",
        "pt": "Melancia",
        "en": "Watermelon",
        "en_som": "Uó-ter-mé-lon",
        "es": "Sandía",
        "es_som": "San-dí-a",
        "icone": "🍉",
        "gesto": "Fresquinha e cheia de água!",
    },
    {
        "id": "carrot",
        "categoria": "comidas",
        "pt": "Cenoura",
        "en": "Carrot",
        "en_som": "Ké-rot",
        "es": "Zanahoria",
        "es_som": "Sa-na-ó-ri-a",
        "icone": "🥕",
        "gesto": "Dá visão de super-herói!",
    },
    {
        "id": "cheese",
        "categoria": "comidas",
        "pt": "Queijo",
        "en": "Cheese",
        "en_som": "Tchiz",
        "es": "Queso",
        "es_som": "Ké-so",
        "icone": "🧀",
        "gesto": "Amarelinho e saboroso!",
    },
    {
        "id": "egg",
        "categoria": "comidas",
        "pt": "Ovo",
        "en": "Egg",
        "en_som": "Ég",
        "es": "Huevo",
        "es_som": "Ué-vo",
        "icone": "🥚",
        "gesto": "Proteína forte dos campeões!",
    },
    # --- SAUDAÇÕES E CARINHO ---
    {
        "id": "hello",
        "categoria": "saudacoes",
        "pt": "Olá",
        "en": "Hello",
        "en_som": "Re-lóu",
        "es": "Hola",
        "es_som": "Ó-la",
        "icone": "👋",
        "gesto": "Acene a mãozinha com um grande sorriso!",
    },
    {
        "id": "good_morning",
        "categoria": "saudacoes",
        "pt": "Bom Dia",
        "en": "Good Morning",
        "en_som": "Gud Mór-nin",
        "es": "Buenos Días",
        "es_som": "Bué-nos Dí-as",
        "icone": "☀️",
        "gesto": "Espreguice os bracinhos como ao acordar!",
    },
    {
        "id": "good_night",
        "categoria": "saudacoes",
        "pt": "Boa Noite",
        "en": "Good Night",
        "en_som": "Gud Náit",
        "es": "Buenas Noches",
        "es_som": "Bué-nas Nó-tches",
        "icone": "🌙",
        "gesto": "Junte as duas mãozinhas na bochecha para dormir!",
    },
    {
        "id": "thank_you",
        "categoria": "saudacoes",
        "pt": "Obrigado",
        "en": "Thank You",
        "en_som": "Tenk Iú",
        "es": "Gracias",
        "es_som": "Grá-si-as",
        "icone": "🙏",
        "gesto": "Mãozinhas no peito em gratidão!",
    },
    {
        "id": "i_love_you",
        "categoria": "saudacoes",
        "pt": "Eu Te Amo",
        "en": "I Love You",
        "en_som": "Ai Lóv Iú",
        "es": "Te Quiero",
        "es_som": "Te Ki-é-ro",
        "icone": "❤️",
        "gesto": "Abrace forte quem você ama!",
    },
    {
        "id": "bye_bye",
        "categoria": "saudacoes",
        "pt": "Tchau Tchau",
        "en": "Bye Bye",
        "en_som": "Bái Bái",
        "es": "Adiós",
        "es_som": "A-di-ós",
        "icone": "👋",
        "gesto": "Mande um beijinho de despedida!",
    },

        {
        "id": "good_afternoon",
        "categoria": "saudacoes",
        "pt": "Boa Tarde",
        "en": "Good Afternoon",
        "en_som": "Gud Áf-ter-nun",
        "es": "Buenas Tardes",
        "es_som": "Bué-nas Tár-des",
        "icone": "🌤️",
        "gesto": "Deseje uma linda tarde!",
    },
    {
        "id": "please",
        "categoria": "saudacoes",
        "pt": "Por Favor",
        "en": "Please",
        "en_som": "Pliz",
        "es": "Por Favor",
        "es_som": "Por Fa-vór",
        "icone": "🤲",
        "gesto": "Palavrinha da gentileza!",
    },
    {
        "id": "welcome",
        "categoria": "saudacoes",
        "pt": "De Nada",
        "en": "You're Welcome",
        "en_som": "Ior Uél-cam",
        "es": "De Nada",
        "es_som": "De Ná-da",
        "icone": "🤝",
        "gesto": "Prazer em ajudar!",
    },
    {
        "id": "how_are_you",
        "categoria": "saudacoes",
        "pt": "Tudo Bem?",
        "en": "How are you?",
        "en_som": "Ráu ár iú?",
        "es": "¿Cómo estás?",
        "es_som": "Kó-mo es-tás?",
        "icone": "😊",
        "gesto": "Com um grande sorriso!",
    },
    {
        "id": "congratulations",
        "categoria": "saudacoes",
        "pt": "Parabéns!",
        "en": "Congrats!",
        "en_som": "Con-gréts!",
        "es": "¡Felicidades!",
        "es_som": "Fe-li-si-dá-des",
        "icone": "🎊",
        "gesto": "Bata palminhas de alegria!",
    },
    {
        "id": "yes_no",
        "categoria": "saudacoes",
        "pt": "Sim e Não",
        "en": "Yes / No",
        "en_som": "Iés / Nôu",
        "es": "Sí / No",
        "es_som": "Si i No",
        "icone": "👍",
        "gesto": "Faça o joinha com o polegar!",
    },
    # --- FAMÍLIA ---
    {
        "id": "dad",
        "categoria": "familia",
        "pt": "Papai",
        "en": "Daddy",
        "en_som": "Dé-di",
        "es": "Papá",
        "es_som": "Pa-pá",
        "icone": "👨",
        "gesto": "O grande herói protetor!",
    },
    {
        "id": "mom",
        "categoria": "familia",
        "pt": "Mamãe",
        "en": "Mommy",
        "en_som": "Mó-mi",
        "es": "Mamá",
        "es_som": "Ma-má",
        "icone": "👩",
        "gesto": "O abraço mais aconchegante!",
    },
    {
        "id": "brother",
        "categoria": "familia",
        "pt": "Irmão",
        "en": "Brother",
        "en_som": "Bró-der",
        "es": "Hermano",
        "es_som": "Er-má-no",
        "icone": "👦",
        "gesto": "Parceiro de aventuras e brincadeiras!",
    },
    {
        "id": "baby",
        "categoria": "familia",
        "pt": "Bebê",
        "en": "Baby",
        "en_som": "Béi-bi",
        "es": "Bebé",
        "es_som": "Be-bé",
        "icone": "👶",
        "gesto": "Faça carinho suave como em um bebezinho!",
    },
    {
        "id": "friend",
        "categoria": "familia",
        "pt": "Amigo",
        "en": "Friend",
        "en_som": "Frénd",
        "es": "Amigo",
        "es_som": "A-mí-go",
        "icone": "🤝",
        "gesto": "Dê um toque de mão ou abraço de amizade!",
    },
    {
        "id": "grandpa",
        "categoria": "familia",
        "pt": "Vovô",
        "en": "Grandpa",
        "en_som": "Grénd-pa",
        "es": "Abuelo",
        "es_som": "A-bué-lo",
        "icone": "👴",
        "gesto": "O vovô querido que conta histórias mágicas!",
    },
    {
        "id": "grandma",
        "categoria": "familia",
        "pt": "Vovó",
        "en": "Grandma",
        "en_som": "Grénd-ma",
        "es": "Abuela",
        "es_som": "A-bué-la",
        "icone": "👵",
        "gesto": "A comidinha mais gostosa do mundo!",
    },
    {
        "id": "sister",
        "categoria": "familia",
        "pt": "Irmã",
        "en": "Sister",
        "en_som": "Sís-ter",
        "es": "Hermana",
        "es_som": "Er-má-na",
        "icone": "👧",
        "gesto": "Parceira de carinho e risadas!",
    },
    {
        "id": "son",
        "categoria": "familia",
        "pt": "Filho",
        "en": "Son",
        "en_som": "Sân",
        "es": "Hijo",
        "es_som": "Í-rro",
        "icone": "👦",
        "gesto": "O filhinho campeão, orgulho do papai e da mamãe!",
    },
    {
        "id": "family",
        "categoria": "familia",
        "pt": "Família",
        "en": "Family",
        "en_som": "Fé-mi-li",
        "es": "Familia",
        "es_som": "Fa-mí-lia",
        "icone": "👨‍👩‍👦",
        "gesto": "Todos unidos com amor incondicional!",
    },
    {
        "id": "home",
        "categoria": "familia",
        "pt": "Nosso Lar",
        "en": "Home",
        "en_som": "Rôum",
        "es": "Hogar",
        "es_som": "O-gár",
        "icone": "🏡",
        "gesto": "A nossa casa quentinha e protegida!",
    },
    {
        "id": "hug",
        "categoria": "familia",
        "pt": "Abraço de Amor",
        "en": "Hug",
        "en_som": "Rág",
        "es": "Abrazo",
        "es_som": "A-brá-so",
        "icone": "🤗",
        "gesto": "Aperte bem forte quem você ama com todo carinho!",
    },
]


# ==============================================================================
# FUNÇÕES DE CONSULTA E GAMEPLAY
# ==============================================================================


def listar_categorias() -> List[Dict]:
    """Retorna todas as categorias disponíveis."""
    return CATEGORIAS


def listar_palavras(idioma: str = "en", categoria: Optional[str] = None) -> List[Dict]:
    """
    Retorna a lista de palavras formatadas para o idioma escolhido ('en' ou 'es').
    """
    idioma = "es" if idioma.lower() == "es" else "en"
    itens = []
    for p in VOCABULARIO:
        if categoria and p["categoria"] != categoria:
            continue
        item = {
            "id": p["id"],
            "categoria": p["categoria"],
            "pt": p["pt"],
            "icone": p["icone"],
            "gesto": p.get("gesto", ""),
            "palavra": p[idioma],
            "pronuncia_som": p[f"{idioma}_som"],
            "idioma": idioma,
        }
        if "numero" in p:
            item["numero"] = p["numero"]
        if "cor_hex" in p:
            item["cor_hex"] = p["cor_hex"]
        if "som_animal" in p:
            item["som_animal"] = p["som_animal"]
        itens.append(item)
    return itens


def gerar_quiz(idioma: str = "en", categoria: Optional[str] = None) -> Dict:
    """
    Sorteia uma pergunta interativa do Jarvis no idioma especificado.
    Retorna a palavra correta e 2 distratores para a criança escolher.
    """
    idioma = "es" if idioma.lower() == "es" else "en"
    pool = [p for p in VOCABULARIO if not categoria or p["categoria"] == categoria]
    if len(pool) < 3:
        pool = VOCABULARIO

    alvo = random.choice(pool)
    distratores = [p for p in VOCABULARIO if p["id"] != alvo["id"]]
    sorteados = random.sample(distratores, 2)

    opcoes = [
        {"id": alvo["id"], "palavra": alvo[idioma], "icone": alvo["icone"], "pt": alvo["pt"]},
        {"id": sorteados[0]["id"], "palavra": sorteados[0][idioma], "icone": sorteados[0]["icone"], "pt": sorteados[0]["pt"]},
        {"id": sorteados[1]["id"], "palavra": sorteados[1][idioma], "icone": sorteados[1]["icone"], "pt": sorteados[1]["pt"]},
    ]
    random.shuffle(opcoes)

    if idioma == "en":
        frase_jarvis = f"Where is the {alvo['en']}? Onde está o {alvo['pt']}?"
        voz_prompt = f"Where is the {alvo['en']}?"
    else:
        frase_jarvis = f"¿Dónde está el {alvo['es']}? Onde está o {alvo['pt']}?"
        voz_prompt = f"Dónde está el {alvo['es']}?"

    return {
        "id_correto": alvo["id"],
        "palavra_alvo": alvo[idioma],
        "palavra_pt": alvo["pt"],
        "icone_alvo": alvo["icone"],
        "idioma": idioma,
        "frase_jarvis": frase_jarvis,
        "voz_prompt": voz_prompt,
        "opcoes": opcoes,
    }


def validar_resposta(palavra_id: str, opcao_escolhida: str, idioma: str = "en") -> Dict:
    """
    Valida a escolha da criança, persiste no SQLite e premia com moedas imediatas.
    """
    idioma = "es" if idioma.lower() == "es" else "en"
    acertou = palavra_id == opcao_escolhida

    # Encontra categoria
    cat = "geral"
    palavra_alvo_texto = palavra_id
    for p in VOCABULARIO:
        if p["id"] == palavra_id:
            cat = p["categoria"]
            palavra_alvo_texto = p[idioma]
            break

    # Registra progresso no banco
    banco_dados.registrar_progresso_idioma(idioma, cat, palavra_id, acertou)

    if acertou:
        # Credita 5 moedas para o Pote do Tesouro
        pote = token_mgr.creditar_fichas(
            quantidade=5,
            motivo=f"Acertou palavra em {idioma.upper()}: {palavra_alvo_texto}",
            categoria="IDIOMAS",
        )
        if idioma == "en":
            elogio = f"Great job, Kaleo! You found the {palavra_alvo_texto}! Ganhou +5 fichas para o seu Pote do Tesouro!"
        else:
            elogio = f"¡Muy bien, Kaleo! ¡Encontraste el {palavra_alvo_texto}! Ganhou +5 fichas para o seu Pote do Tesouro!"

        return {
            "acertou": True,
            "mensagem": elogio,
            "fichas_ganhas": 5,
            "saldo_pote": pote.get("saldo", 0),
            "palavra_correta": palavra_alvo_texto,
        }
    else:
        if idioma == "en":
            dica = f"Almost there! Vamos tentar mais uma vez juntos, pequeno herói!"
        else:
            dica = f"¡Casi, casi! ¡Vamos a intentarlo otra vez juntos, pequeño héroe!"

        return {
            "acertou": False,
            "mensagem": dica,
            "fichas_ganhas": 0,
            "palavra_correta": palavra_alvo_texto,
        }
