<script lang="ts">
	import '../app.css';
    import { Navbar, NavBrand, NavLi, NavUl, NavHamburger, Button, Input } from 'flowbite-svelte';

    let { children } = $props();
</script>
<nav class="my-custom-navbar bg-blend-lighten px-4 py-2 flex justify-between items-center">
    <NavBrand href="/">
        <span class="whitespace-nowrap text-xl font-semibold text-primary-500">Terminal</span>
    </NavBrand>
    <NavUl class="hidden md:flex gap-4">
<!--        <NavLi href="/">Главная</NavLi>-->
    </NavUl>
    <div class="flex gap-2 items-center">
        <div class="flex flex-row gap-2 items-center">
            <a href="/accounts/register" class="cursor-pointer text-center font-medium focus-within:ring-4 focus-within:outline-hidden inline-flex items-center justify-center px-5 py-2.5 text-sm text-white bg-primary-700 hover:bg-primary-800 focus-within:ring-primary-300  rounded-lg">Регистрация</a>
            <a href="/accounts/login" class="cursor-pointer text-center font-medium focus-within:ring-4 focus-within:outline-hidden inline-flex items-center justify-center px-5 py-2.5 text-sm text-primary-700 bg-white border-1 hover:bg-primary-800 hover:text-white focus-within:ring-primary-300 rounded-lg">Войти</a>
        </div>
        <NavHamburger />
    </div>
</nav>
{@render children()}
