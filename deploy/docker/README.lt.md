# Diegimas naudojant *Docker*

## Apie

`Chat demo` aplikacija yra realizuota *Docker* komponentais. Visa sistema sukonfigūruota ir paruošta paleisti su *docker compose* konfigūraciniu failu.


## Reikalavimai

### Aparatūrai

| Komponen-tas | Min reikalavimai | Rekomenduo-jama | Papildomai |
| -----------------|------------------|---------------------|-------------------------------------------|
| Platform | x86_64 | | |
| CPU | 64-bit, 2 branduoliai | 4 branduoliai | |
| HDD | 10 Gb | 15Gb  | |
| RAM | 4 Gb | 8 Gb | |

### Programinei įrangai

#### OS

Linux OS 64-bit (papildomai žiūrėkite [reikalavimus Docker instaliacijai](https://docs.docker.com/engine/install/)). Reckomenduojama `Debian Bookworm 12 (stable)`. 


#### Kiti

| Komponentas | Min versija | URL |
| ---|-|-|
| Docker | 27.0.3 | [Link](https://docs.docker.com/engine/install/)

Papildomi įrankiai naudojami instaliuojant: [make](https://www.gnu.org/software/make/manual/make.html).

### Tinklas

- Pasiekiami port'ai: `443`, `80`.
- Diegimui prisijungimas per ssh: portas `22`
- Domenas

### Vartotojas

Vartotojas kuris diegia, turi turėti `root` teises.

## Prieš diegiant

Patikrinkite ar visi reikalingi komponentai veikia mašinoje:

```bash
    ## Docker
    docker run hello-world
    docker system info
    ## Kiti komponentai
    make --version
```   
 
Ar domenas sukonfigūruotas teisingai. Patikriname iš kitos mašinos:
```bash
    dig <domain>
```

## Diegimas

...TODO
