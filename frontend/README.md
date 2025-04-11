# frontend

This template should help get you started developing with Vue 3 in Vite.

---

## Important! How to contribute to this project

- step1: check out a new branch:

```sh
git checkout -b 'your_branch_name'
```

- step2: write your components in directories `src/views` or `src/components`
    > It is recommended that the `view` directory contains the first-level components that router routes, while the `components` directory contains components that your `view/*` components imports. 

- optional step3: if necessary, modify `src/router/index.js` to add your view to a new route.

- step4: commit, push to your own branch, issue a PR to merge to branch master

---

## Topology

Please refer to `documents/topology.drawio` to check for latest updates.

Top component is `src/App.vue`, responsible for top and left navigation bar / drawer. It imports `router view`.

The next components is registered using vue router. Depending on the url that access the system, the components imported will be in the range of the following:
- [ / ] `views/Home.vue`
- [ /dev ] `views/Dev.vue`
- [ /plan ] `views/Plan.vue`

---

## Customize configuration

See [Vite Configuration Reference](https://vitejs.dev/config/).

## Project Setup

```sh
npm install
```

### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Compile and Minify for Production

```sh
npm run build
```
