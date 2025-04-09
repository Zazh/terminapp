<script>
    import { Label, Input, Button } from 'flowbite-svelte';
    import { EnvelopeSolid } from 'flowbite-svelte-icons';

    let email = '';
    let emailError = '';
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    function handleSubmit() {
        emailError = '';

        if (!emailRegex.test(email)) {
            emailError = 'Введите корректный email.';
        }

    }
</script>

<section class="max-w-md mx-auto pt-15">
    <div class="pb-5">
        <h1 class="text-[2.5rem] font-semibold">Забыли пароль</h1>
        <div class="mt-1 flex gap-2">
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
            <Button size="xl" class="text-sm cursor-pointer font-bold w-full rounded-md" on:click={handleSubmit}>Восстановить доступ</Button>
        </div>
    </div>
</section>