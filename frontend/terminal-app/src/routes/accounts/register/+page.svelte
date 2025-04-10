<script>
    import { Label, Input, Button } from 'flowbite-svelte';
    import { EnvelopeSolid, EyeOutline, EyeSlashOutline } from 'flowbite-svelte-icons';

    let email = '';
    let password = '';
    let confirmPassword = '';
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
        } else if (password !== confirmPassword) {
            passwordError = 'Пароли не совпадают.';
        }

        if (!emailError && !passwordError) {
            alert('Форма успешно отправлена!');
        }
    }
</script>

<section class="max-w-md mx-auto pt-[15rem]">
    <div class="pb-5">
        <h1 class="text-[3rem] font-semibold">Регистрация</h1>
    </div>
    <div class="flex flex-wrap gap-4">
        <div class="w-full">
            <Label for="email" class="mb-1 font-bold">Электронная почта</Label>
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

        {#if password}
        <div class="w-full">
            <Label for="confirm-password" class="mb-1 font-bold">Повторите пароль</Label>
            <Input id="confirm-password"
                   type={show ? 'text' : 'password'}
                   placeholder="••••••••••"
                   bind:value={confirmPassword}
                   size="md"
                   color={passwordError ? 'red' : 'base'}>
                <button slot="left" on:click={() => (show = !show)} class="pointer-events-auto">
                    {#if show}
                        <EyeOutline class="w-5 h-5" />
                    {:else}
                        <EyeSlashOutline class="w-5 h-5" />
                    {/if}
                </button>
            </Input>
            {#if passwordError}
                <p class="text-sm text-red-600 mt-1">{passwordError}</p>
            {/if}
        </div>
        {/if}

        <div class="w-full pt-2">
            <Button size="xl" class="text-sm cursor-pointer font-bold w-full rounded-md" on:click={handleSubmit}>Зарегистрироваться</Button>
        </div>

        <div class="w-full text-center mt-5">
            <div class="pt-5 flex justify-center gap-2 border-gray-200 border-t-1">
                <span class="text-md font-medium text-gray-600">Уже есть аккаунта?</span>
                <a href="/accounts/login" class="text-blue-600 hover:text-blue-700 font-medium text-md">Войти</a>
            </div>
        </div>
    </div>
</section>