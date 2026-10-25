import random

POTION_SLOTS = 10
INGREDIENT_SLOTS = 25
POTION_STACK_LIMIT = 10
INGREDIENT_STACK_LIMIT = 25
DAILY_INGREDIENT_REWARD = 5

INGREDIENT_POOL = [f"Інгредієнт_{i}" for i in range(1, 201)]
POTION_POOL = {
    f"Зілля_{i}": {
        "recipe": {f"Інгредієнт_{i}": 2, f"Інгредієнт_{(i % 200) + 1}": 1},
        "price": 50 + (i * 2)
    } for i in range(1, 51)
}

WIN_GOLD = 1000
MAX_DAYS = 20
START_GOLD = 100


class RPGGameException(Exception):
    """Базове виключення для гри"""
    pass


class InventoryFullException(RPGGameException):
    """Помилка місця в інвентарі"""
    pass


class ItemNotFoundException(RPGGameException):
    """Помилка відсутності предмета"""
    pass


class InsufficientIngredientsException(RPGGameException):
    """Бракує інгредієнтів для крафту"""
    pass


class InvalidInputException(RPGGameException):
    """Некоректне введення команди"""
    pass


class Inventory:
    def __init__(self, max_slots, stack_limit, name):
        self.max_slots = max_slots
        self.stack_limit = stack_limit
        self.name = name
        self.slots = {}

    def add_item(self, item_name, amount=1):
        try:
            if amount <= 0:
                return

            current_slots_used = sum((qty + self.stack_limit - 1) // self.stack_limit for qty in self.slots.values())

            if item_name in self.slots:
                current_qty = self.slots[item_name]
                space_in_existing_stacks = (self.stack_limit - (current_qty % self.stack_limit)) % self.stack_limit

                if amount <= space_in_existing_stacks:
                    self.slots[item_name] += amount
                    return
                else:
                    self.slots[item_name] += space_in_existing_stacks
                    amount -= space_in_existing_stacks

            needed_slots = (amount + self.stack_limit - 1) // self.stack_limit

            if current_slots_used + needed_slots > self.max_slots:
                raise InventoryFullException(f"Не вистачає місця в інвентарі {self.name}!")

            if item_name in self.slots:
                self.slots[item_name] += amount
            else:
                self.slots[item_name] = amount
        except KeyError:
            print("[Помилка конфігурації інвентаря]")

    def remove_item(self, item_name, amount=1):
        try:
            if item_name not in self.slots or self.slots[item_name] < amount:
                raise ItemNotFoundException(f"Недостатньо предметів '{item_name}' в інвентарі {self.name}.")

            self.slots[item_name] -= amount
            if self.slots[item_name] == 0:
                del self.slots[item_name]
        except KeyError:
            raise ItemNotFoundException("Предмет не знадено.")

    def show(self):
        if not self.slots:
            print("  Порожньо")
            return
        for item, qty in self.slots.items():
            slots_occupied = (qty + self.stack_limit - 1) // self.stack_limit
            print(f"  - {item}: {qty} шт. (Займає слотів: {slots_occupied})")

class GameMechanics:
    def __init__(self, ingredient_inv, potion_inv):
        self.ing_inv = ingredient_inv
        self.pot_inv = potion_inv
        self.gold = START_GOLD
        self.day = 1

    def start_new_day(self):
        print(f"\n=== ПОЧАТОК ДНЯ {self.day} ===")
        print("Вам нараховано щоденні інгредієнти:")
        for _ in range(DAILY_INGREDIENT_REWARD):
            try:
                ing = random.choice(INGREDIENT_POOL)
                self.ing_inv.add_item(ing, 1)
                print(f" + Отримано: {ing}")
            except InventoryFullException as e:
                print(f" [Увага] Не вдалося отримати інгредієнт: {e}")

    def craft_potion(self, potion_name):
        try:
            if potion_name not in POTION_POOL:
                raise KeyError("Такого зілля не існує в алхімічній книзі.")

            recipe = POTION_POOL[potion_name]["recipe"]

            for ing, count in recipe.items():
                if self.ing_inv.slots.get(ing, 0) < count:
                    raise InsufficientIngredientsException(f"Бракує інгредієнту {ing} для {potion_name}.")

            self.pot_inv.add_item(potion_name, 1)

            for ing, count in recipe.items():
                self.ing_inv.remove_item(ing, count)

            print(f" Успішно зварено: {potion_name}!")

        except (InsufficientIngredientsException, InventoryFullException) as e:
            print(f" [Помилка крафту] {e}")
        except KeyError as e:
            print(f" [Помилка] {e}")

    def sell_all_potions(self):
        try:
            potions_to_sell = list(self.pot_inv.slots.items())
            if not potions_to_sell:
                print("У вас немає зілля для продажу.")
                return

            total_earned = 0
            for potion_name, qty in potions_to_sell:
                price = POTION_POOL[potion_name]["price"]
                earnings = price * qty
                total_earned += earnings
                self.pot_inv.remove_item(potion_name, qty)
                print(f" Продано {potion_name} x{qty} за {earnings} золота.")

            self.gold += total_earned
            print(f"Усього зароблено за день: {total_earned} золота!")
        except ItemNotFoundException as e:
            print(f" [Помилка продажу] {e}")

    def check_game_status(self):
        if self.gold >= WIN_GOLD:
            return "WIN"
        if self.day >= MAX_DAYS:
            return "LOSE"
        return "CONTINUE"


def print_help():
    print("\nДоступні команди:")
    print(" 1 - Показати стан (золото, день, інвентарі)")
    print(" 2 - Переглянути книгу рецептів зілля")
    print(" 3 - Зварити (скрафтити) зілля")
    print(" 4 - Завершити день (продати зілля та перейти до наступного)")
    print(" 0 - Вийти з гри")


def main():
    print("====================================================")
    print(" ЛАБОРАТОРНА РОБОТА №5: СИМУЛЯТОР АЛХІМІКА ")
    print(f" Мета: Накопичити {WIN_GOLD} золота за менш ніж {MAX_DAYS} днів.")
    print("====================================================")

    ing_inventory = Inventory(INGREDIENT_SLOTS, INGREDIENT_STACK_LIMIT, "Інгредієнтів")
    pot_inventory = Inventory(POTION_SLOTS, POTION_STACK_LIMIT, "Зілля")
    game = GameMechanics(ing_inventory, pot_inventory)

    game.start_new_day()

    while True:
        try:
            status = game.check_game_status()
            if status == "WIN":
                print(f"\n Найсвятіший Мерлін! Ви накопичили {game.gold} золота! ВИ ВИГРАЛИ ГРУ! ")
                break
            elif status == "LOSE":
                print(f"\n Час вийшов (Минуло {MAX_DAYS} днів). Ви оголошені банкрутом. ВИ ПРОГРАЛИ! ")
                break

            print_help()
            choice = input("Оберіть дію: ").strip()

            if choice == "1":
                print(f"\n--- СТАН АЛХІМІКА (День {game.day}) ---")
                print(f"Золото: {game.gold} / {WIN_GOLD}")
                print("Інвентар інгредієнтів:")
                ing_inventory.show()
                print("Інвентар зілля:")
                pot_inventory.show()

            elif choice == "2":
                print("\n--- АЛХІМІЧНА КНИГА РЕЦЕПТІВ (Перші 5) ---")
                keys = list(POTION_POOL.keys())[:5]
                for key in keys:
                    recipe_str = ", ".join([f"{k} x{v}" for k, v in POTION_POOL[key]['recipe'].items()])
                    print(f" * {key} | Рецепт: [{recipe_str}] | Ціна: {POTION_POOL[key]['price']} золота")
                print("... та ще 45 унікальних рецептів у базі даних.")

            elif choice == "3":
                potion_to_craft = input("Введіть точну назву зілля (напр., Зілля_1): ").strip()
                game.craft_potion(potion_to_craft)

            elif choice == "4":
                print("\n Настає вечір. Ви вирушаєте на ринок...")
                game.sell_all_potions()
                game.day += 1
                game.start_new_day()

            elif choice == "0":
                print("Дякуємо за гру! Вихід...")
                break
            else:
                raise InvalidInputException("Невірна команда! Введіть число від 0 до 4.")

        except InvalidInputException as e:
            print(f" [Помилка введення] {e}")
        except Exception as e:
            print(f" [Критична помилка системи] {e}")


if __name__ == "__main__":
    main()
