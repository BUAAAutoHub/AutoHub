import Vue from 'vue';
import Vuetify from 'vuetify';
import 'vuetify/dist/vuetify.min.css';
import zhHans from 'vuetify/lib/locale/zh-Hans';
import '@mdi/font/css/materialdesignicons.css'

Vue.use(Vuetify);

export default new Vuetify({
    lang: {
      locales: { zhHans },
      current: 'zhHans',
    },
    icons: {
        defaultSet: 'mdi',
    }
});
