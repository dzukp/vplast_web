
const { createApp, ref } = Vue


const app = Vue.createApp({
  data() {
    return {
      serverName: '',
      params: [],
      serverId: 1,
      servers: {
        1: 'Линия 4',
        2: 'Линия 5',
        3: 'Линия X',
      }
    };
  },
  mounted() {
    this.fetchData();

    const appElement = document.getElementById("app");
    const hammer = new Hammer(appElement);

    hammer.on("swipeleft", () => {
      this.changeServerId(this.serverId - 1);
    });

    hammer.on("swiperight", () => {
      this.changeServerId(this.serverId + 1);
    });
  },
  methods: {

    async fetchData() {
      try {
        const response = await fetch('/api/get-params?id=' + this.serverId);
        const response_data = await response.json();

        this.serverName = this.servers[this.serverId]

        this.params = response_data.map(item => {

          return {
            name: item.name,
            value: item.value,
            status: item.status
          };
        });

      } catch (error) {
        console.error('Ошибка при получении данных:', error);
      }

      setTimeout(this.fetchData, 500);
    },

    changeServerId(newServerId) {
      if (this.serverId != newServerId) {
        if (this.servers[newServerId] != undefined)
          this.serverId = newServerId;
//          this.fetchData();
      }
    },
  },


});

app.mount('#app')