<script lang="ts">
	import '../app.css';
    import { Navbar, NavBrand, NavLi, NavUl, NavHamburger, Button, Input } from 'flowbite-svelte';

    let { children } = $props();
</script>
<nav class="my-custom-navbar bg-blend-lighten px-4 py-2 flex justify-between items-center">
    <NavBrand href="/">
        <span class="whitespace-nowrap text-xl font-semibold text-primary-500">Flowbite</span>
    </NavBrand>
    <NavUl class="hidden md:flex gap-4">
        <NavLi href="/" active={true}>Home</NavLi>
        <NavLi href="/about">About</NavLi>
        <NavLi href="/docs/components/navbar">Navbar</NavLi>
        <NavLi href="/pricing">Pricing</NavLi>
        <NavLi href="/contact">Contact</NavLi>
    </NavUl>
    <div class="flex gap-2 items-center">
        <Button size="sm">Get started</Button>
        <NavHamburger />
    </div>
</nav>
{@render children()}
