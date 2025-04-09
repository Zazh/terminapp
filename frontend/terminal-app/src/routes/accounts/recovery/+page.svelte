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
        <h1 class="text-[2.5rem] font-semibold">Забыли пароль</h1>
        <div class="mt-1 flex justify-center gap-2">
            <span class="text-md font-medium text-gray-600">На почту придет ссылка для сброса пароля</span>
        </div>
    </div>
    <div class="flex flex-wrap gap-4">
        <div class="w-full">
            <Label for="email" class="mb-1 font-bold">Введите Email</Label>
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
        <div class="text-center mt-2 w-full">
            <Button size="xl" class="text-sm cursor-pointer font-bold w-full rounded-full" on:click={handleSubmit}>Восстановить доступ</Button>
        </div>
    </div>
</section>