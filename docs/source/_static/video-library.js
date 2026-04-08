(function () {
  const STORAGE_PREFIX = "flask-commands.video.watched.";
  const API_SRC = "https://www.youtube.com/iframe_api";
  const players = new Map();
  const runtimeStates = new Map();
  let apiRequested = false;
  let apiReady = false;

  const VIDEO_STATE = {
    UNWATCHED: "unwatched",
    WATCHING: "watching",
    WATCHED: "watched",
  };

  function storageKey(videoKey) {
    return STORAGE_PREFIX + videoKey;
  }

  function getVideoState(videoKey) {
    if (runtimeStates.get(videoKey) === VIDEO_STATE.WATCHING) {
      return VIDEO_STATE.WATCHING;
    }
    const stored = window.localStorage.getItem(storageKey(videoKey));
    if (stored === VIDEO_STATE.WATCHING || stored === VIDEO_STATE.WATCHED) {
      return stored === VIDEO_STATE.WATCHING ? VIDEO_STATE.UNWATCHED : stored;
    }
    if (stored === "true") {
      return VIDEO_STATE.WATCHED;
    }
    return VIDEO_STATE.UNWATCHED;
  }

  function setVideoState(videoKey, state) {
    if (state === VIDEO_STATE.WATCHED) {
      runtimeStates.delete(videoKey);
      window.localStorage.setItem(storageKey(videoKey), VIDEO_STATE.WATCHED);
    } else if (state === VIDEO_STATE.WATCHING) {
      runtimeStates.set(videoKey, VIDEO_STATE.WATCHING);
    } else {
      runtimeStates.delete(videoKey);
      window.localStorage.removeItem(storageKey(videoKey));
    }
    syncVideoState(videoKey, state);
  }

  function syncVideoState(videoKey, state) {
    document.querySelectorAll('.fc-video-card[data-video-key="' + videoKey + '"]').forEach((card) => {
      const isWatching = state === VIDEO_STATE.WATCHING;
      const isWatched = state === VIDEO_STATE.WATCHED;
      card.classList.toggle("is-watching", isWatching);
      card.classList.toggle("is-watched", isWatched);
      const stateLabel = card.querySelector(".fc-video-state");
      if (stateLabel) {
        stateLabel.textContent = isWatched ? "Watched" : isWatching ? "Watching..." : "Unwatched";
      }
    });

    document.querySelectorAll('.fc-video-checkbox[data-video-key="' + videoKey + '"]').forEach((checkbox) => {
      checkbox.setAttribute(
        "aria-checked",
        state === VIDEO_STATE.WATCHING ? "mixed" : state === VIDEO_STATE.WATCHED ? "true" : "false"
      );
    });
  }

  function syncAllCards() {
    document.querySelectorAll(".fc-video-card[data-video-key]").forEach((card) => {
      syncVideoState(card.dataset.videoKey, getVideoState(card.dataset.videoKey));
    });
  }

  function toggleWatchedState(videoKey) {
    const currentState = getVideoState(videoKey);
    setVideoState(videoKey, currentState === VIDEO_STATE.WATCHED ? VIDEO_STATE.UNWATCHED : VIDEO_STATE.WATCHED);
  }

  function eventHitsCheckbox(card, event) {
    const checkboxVisual = card.querySelector(".fc-video-checkbox-wrap");
    if (!checkboxVisual || typeof event.clientX !== "number" || typeof event.clientY !== "number") {
      return false;
    }

    const rect = checkboxVisual.getBoundingClientRect();
    const padding = 6;
    return (
      event.clientX >= rect.left - padding &&
      event.clientX <= rect.right + padding &&
      event.clientY >= rect.top - padding &&
      event.clientY <= rect.bottom + padding
    );
  }

  function wireCheckboxes() {
    document.querySelectorAll(".fc-video-checkbox").forEach((checkbox) => {
      if (checkbox.dataset.bound === "true") {
        return;
      }

      checkbox.dataset.bound = "true";
      const blockCardToggle = function (event) {
        event.preventDefault();
        event.stopPropagation();
      };

      checkbox.addEventListener("pointerdown", blockCardToggle);
      checkbox.addEventListener("mousedown", blockCardToggle);
      checkbox.addEventListener("mouseup", blockCardToggle);
      checkbox.addEventListener("touchstart", blockCardToggle, { passive: false });
      checkbox.addEventListener("touchend", blockCardToggle, { passive: false });
      checkbox.addEventListener("click", (event) => {
        event.preventDefault();
        event.stopPropagation();
        const videoKey = event.currentTarget.dataset.videoKey;
        toggleWatchedState(videoKey);
      });
    });
  }

  function wireSummaries() {
    document.querySelectorAll(".fc-video-card > .fc-video-summary").forEach((summary) => {
      if (summary.dataset.bound === "true") {
        return;
      }

      summary.dataset.bound = "true";
      const interceptSummaryToggle = function (event) {
        const card = summary.closest(".fc-video-card");
        if (!card || !eventHitsCheckbox(card, event)) {
          return;
        }

        event.preventDefault();
        event.stopPropagation();
      };

      summary.addEventListener("pointerdown", interceptSummaryToggle);
      summary.addEventListener("click", (event) => {
        const card = summary.closest(".fc-video-card");
        if (!card || !eventHitsCheckbox(card, event)) {
          return;
        }

        interceptSummaryToggle(event);
        toggleWatchedState(card.dataset.videoKey);
      });
    });
  }

  function ensureFrameLoaded(card) {
    const mount = card.querySelector(".fc-youtube-player");
    if (!mount || mount.dataset.loaded === "true") {
      return;
    }

    const videoId = mount.dataset.videoId;
    if (!videoId) {
      return;
    }

    mount.dataset.loaded = "true";
    requestYoutubeApi();

    if (apiReady) {
      initPlayers();
    }
  }

  function requestYoutubeApi() {
    if (apiRequested) {
      return;
    }

    apiRequested = true;
    const tag = document.createElement("script");
    tag.src = API_SRC;
    tag.async = true;
    document.head.appendChild(tag);
  }

  function initPlayers() {
    if (!apiReady || !window.YT || !window.YT.Player) {
      return;
    }

    document.querySelectorAll('.fc-youtube-player[data-loaded="true"]').forEach((mount) => {
      if (players.has(mount.id) || !mount.id) {
        return;
      }

      const videoKey = mount.dataset.videoKey;
      const videoId = mount.dataset.videoId;
      if (!videoId) {
        return;
      }

      const player = new window.YT.Player(mount.id, {
        host: "https://www.youtube.com",
        width: "100%",
        height: "100%",
        videoId: videoId,
        playerVars: {
          rel: 0,
          origin: window.location.origin,
        },
        events: {
          onStateChange: function (event) {
            if (event.data === window.YT.PlayerState.ENDED) {
              setVideoState(videoKey, VIDEO_STATE.WATCHED);
            } else if (event.data === window.YT.PlayerState.PLAYING) {
              setVideoState(videoKey, VIDEO_STATE.WATCHING);
            } else if (
              event.data === window.YT.PlayerState.PAUSED ||
              event.data === window.YT.PlayerState.CUED ||
              event.data === window.YT.PlayerState.UNSTARTED
            ) {
              const persistedState = window.localStorage.getItem(storageKey(videoKey));
              setVideoState(
                videoKey,
                persistedState === VIDEO_STATE.WATCHED ? VIDEO_STATE.WATCHED : VIDEO_STATE.UNWATCHED
              );
            }
          },
        },
      });

      players.set(mount.id, player);
    });
  }

  window.onYouTubeIframeAPIReady = function () {
    apiReady = true;
    initPlayers();
  };

  document.addEventListener("DOMContentLoaded", function () {
    wireCheckboxes();
    wireSummaries();
    syncAllCards();
    document.querySelectorAll(".fc-video-card").forEach((card) => {
      if (card.open) {
        ensureFrameLoaded(card);
      }

      card.addEventListener("toggle", function () {
        if (card.open) {
          ensureFrameLoaded(card);
        }
      });
    });
  });
})();
