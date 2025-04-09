<script>
    import { Label, Input, Button, Checkbox } from 'flowbite-svelte';
    import { EnvelopeSolid, EyeOutline, EyeSlashOutline } from 'flowbite-svelte-icons';

    let email = '';
    let password = '';
    let show = false;

    let emailError = '';
    let passwordError = '';

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    function handleSubmit() {
        emailError = '';
        passwordError = '';

        if (!emailRegex.test(email)) {
            emailError = 'Введите корректный email.';
        }

        if (password.length < 8) {
            passwordError = 'Пароль должен быть не менее 8 символов.';
        }

        if (!emailError && !passwordError) {
            alert('Форма успешно отправлена!');
            // Здесь можно отправить данные на сервер
        }
    }
</script>

<section class="max-w-md mx-auto pt-15">
    <div class="pb-5 text-center">
        <h1 class="text-[2.5rem] font-semibold">С возвращением!</h1>
        <div class="mt-1 flex justify-center gap-2">
            <span class="text-md font-medium text-gray-600">Нет аккаунта?</span>
            <a href="/accounts/register" class="text-blue-600 hover:text-blue-700 font-medium text-md">Зарегестрируйтесь сейчас</a>
        </div>
    </div>
    <div class="flex flex-wrap gap-4">
        <div class="w-full">
            <Label for="email" class="mb-1 font-bold">Email</Label>
            <Input
                    type="email"
                    id="email"
                    placeholder="name@email.com"
                    bind:value={email}
                    size="md"
                    color={emailError ? 'red' : 'base'}>
                <EnvelopeSolid slot="left" class="w-5 h-5" />
            </Input>
            {#if emailError}
                <p class="text-sm text-red-600 mt-1">{emailError}</p>
            {/if}
        </div>
        <div class="w-full">
            <Label for="show-password" class="mb-1 font-bold">Пароль</Label>
            <Input id="show-password"
                   type={show ? 'text' : 'password'}
                   placeholder="••••••••••"
                   bind:value={password}
                   color={passwordError ? 'red' : 'base'}
                   size="md">
                <button slot="left" on:click={() => (show = !show)} class="pointer-events-auto">
                    {#if show}
                        <EyeOutline class="w-5 h-5" />
                    {:else}
                        <EyeSlashOutline class="w-5 h-5" />
                    {/if}
                </button>
            </Input>
        </div>
        <div class="w-full [ flex justify-between my-2 ]">
            <span class="flex items-center gap-2">
                <Checkbox id="remind_me" />
                <label for="remind_me" class="leading-0 text-sm font-semibold cursor-pointer">Запомнить меня</label>
            </span>
            <span>
                <a href="/account/recovery" class="text-blue-600 hover:text-blue-700 font-semibold text-sm">Забыли пароль?</a>
            </span>
        </div>
        <div class="w-full text-center mt-2">
            <Button size="xl" class="text-sm cursor-pointer font-bold w-full rounded-full" on:click={handleSubmit}>Войти</Button>
        </div>
    </div>
</section>