from models import DefinedHeadsign, Station

STATION_DELTAS: dict[Station, dict[DefinedHeadsign, dict[Station, int]]] = {
  Station.NEWARK: {
    DefinedHeadsign.WORLD_TRADE_CENTER: {
      Station.HARRISON: 120,
      Station.JOURNAL_SQUARE: 780,
      Station.GROVE_STREET: 1020,
      Station.EXCHANGE_PLACE: 1200,
      Station.WORLD_TRADE_CENTER: 1500,
    }
  },
  Station.HARRISON: {
    DefinedHeadsign.WORLD_TRADE_CENTER: {
      Station.JOURNAL_SQUARE: 660,
      Station.GROVE_STREET: 900,
      Station.EXCHANGE_PLACE: 1080,
      Station.WORLD_TRADE_CENTER: 1380,
    },
    DefinedHeadsign.NEWARK: {Station.NEWARK: 120},
  },
  Station.JOURNAL_SQUARE: {
    DefinedHeadsign.WORLD_TRADE_CENTER: {
      Station.GROVE_STREET: 240,
      Station.EXCHANGE_PLACE: 420,
      Station.WORLD_TRADE_CENTER: 720,
    },
    DefinedHeadsign.NEWARK: {Station.HARRISON: 660, Station.NEWARK: 780},
    DefinedHeadsign.THIRTY_THIRD_STREET: {
      Station.GROVE_STREET: 240,
      Station.NEWPORT: 480,
      Station.CHRISTOPHER_STREET: 960,
      Station.NINTH_STREET: 1020,
      Station.FOURTEENTH_STREET: 1140,
      Station.TWENTY_THIRD_STREET: 1200,
      Station.THIRTY_THIRD_STREET: 1380,
    },
    DefinedHeadsign.THIRTY_THIRD_VIA_HOBOKEN: {
      Station.GROVE_STREET: 240,
      Station.NEWPORT: 480,
      Station.HOBOKEN: 960,
      Station.CHRISTOPHER_STREET: 960 + 540,
      Station.NINTH_STREET: 960 + 600,
      Station.FOURTEENTH_STREET: 960 + 720,
      Station.TWENTY_THIRD_STREET: 960 + 780,
      # Station.THIRTY_THIRD_STREET: 960 + 960
    },
  },
  Station.GROVE_STREET: {
    DefinedHeadsign.WORLD_TRADE_CENTER: {
      Station.EXCHANGE_PLACE: 180,
      Station.WORLD_TRADE_CENTER: 480,
    },
    DefinedHeadsign.NEWARK: {
      Station.JOURNAL_SQUARE: 240,
      Station.HARRISON: 900,
      Station.NEWARK: 1020,
    },
    DefinedHeadsign.JOURNAL_SQUARE: {Station.JOURNAL_SQUARE: 240},
    DefinedHeadsign.THIRTY_THIRD_STREET: {
      Station.NEWPORT: 240,
      Station.CHRISTOPHER_STREET: 720,
      Station.NINTH_STREET: 780,
      Station.FOURTEENTH_STREET: 900,
      Station.TWENTY_THIRD_STREET: 960,
      Station.THIRTY_THIRD_STREET: 1140,
    },
    DefinedHeadsign.JOURNAL_SQUARE_VIA_HOBOKEN: {
      # Station.JOURNAL_SQUARE: 240
    },
    DefinedHeadsign.THIRTY_THIRD_VIA_HOBOKEN: {
      Station.NEWPORT: 240,
      Station.HOBOKEN: 720,
      Station.CHRISTOPHER_STREET: 720 + 540,
      Station.NINTH_STREET: 720 + 600,
      Station.FOURTEENTH_STREET: 720 + 720,
      Station.TWENTY_THIRD_STREET: 720 + 780,
      # Station.THIRTY_THIRD_STREET: 720 + 960
    },
  },
  Station.EXCHANGE_PLACE: {
    DefinedHeadsign.WORLD_TRADE_CENTER: {Station.WORLD_TRADE_CENTER: 300},
    DefinedHeadsign.NEWARK: {
      Station.GROVE_STREET: 180,
      Station.JOURNAL_SQUARE: 420,
      Station.HARRISON: 1080,
      Station.NEWARK: 1200,
    },
    DefinedHeadsign.JOURNAL_SQUARE: {
      Station.GROVE_STREET: 180,
      Station.JOURNAL_SQUARE: 420,
    },
    DefinedHeadsign.HOBOKEN: {Station.NEWPORT: 180, Station.HOBOKEN: 420},
    DefinedHeadsign.JOURNAL_SQUARE_VIA_HOBOKEN: {  # special case for when Journal Square via Hoboken trains make extra stop at EXP
      Station.GROVE_STREET: 180,
      # Station.JOURNAL_SQUARE: 420,
    },
  },
  Station.WORLD_TRADE_CENTER: {
    DefinedHeadsign.NEWARK: {
      Station.EXCHANGE_PLACE: 300,
      Station.GROVE_STREET: 480,
      Station.JOURNAL_SQUARE: 720,
      Station.HARRISON: 1380,
      Station.NEWARK: 1500,
    },
    DefinedHeadsign.JOURNAL_SQUARE: {
      Station.EXCHANGE_PLACE: 300,
      Station.GROVE_STREET: 480,
      Station.JOURNAL_SQUARE: 720,
    },
    DefinedHeadsign.HOBOKEN: {
      Station.EXCHANGE_PLACE: 300,
      Station.NEWPORT: 480,
      Station.HOBOKEN: 720,
    },
  },
  Station.NEWPORT: {
    DefinedHeadsign.THIRTY_THIRD_STREET: {
      Station.CHRISTOPHER_STREET: 480,
      Station.NINTH_STREET: 540,
      Station.FOURTEENTH_STREET: 660,
      Station.TWENTY_THIRD_STREET: 720,
      Station.THIRTY_THIRD_STREET: 900,
    },
    DefinedHeadsign.JOURNAL_SQUARE: {
      Station.GROVE_STREET: 240,
      Station.JOURNAL_SQUARE: 480,
    },
    DefinedHeadsign.JOURNAL_SQUARE_VIA_HOBOKEN: {
      Station.GROVE_STREET: 240,
      # Station.JOURNAL_SQUARE: 480
    },
    DefinedHeadsign.WORLD_TRADE_CENTER: {
      Station.EXCHANGE_PLACE: 180,
      Station.WORLD_TRADE_CENTER: 480,
    },
    DefinedHeadsign.HOBOKEN: {Station.HOBOKEN: 240},
    DefinedHeadsign.THIRTY_THIRD_VIA_HOBOKEN: {
      Station.HOBOKEN: 480,
      Station.CHRISTOPHER_STREET: 480 + 540,
      Station.NINTH_STREET: 480 + 600,
      Station.FOURTEENTH_STREET: 480 + 720,
      Station.TWENTY_THIRD_STREET: 480 + 780,
      # Station.THIRTY_THIRD_STREET: 480 + 960
    },
  },
  Station.CHRISTOPHER_STREET: {
    DefinedHeadsign.THIRTY_THIRD_STREET: {
      Station.NINTH_STREET: 60,
      Station.FOURTEENTH_STREET: 180,
      Station.TWENTY_THIRD_STREET: 240,
      Station.THIRTY_THIRD_STREET: 420,
    },
    DefinedHeadsign.THIRTY_THIRD_VIA_HOBOKEN: {
      Station.NINTH_STREET: 60,
      Station.FOURTEENTH_STREET: 180,
      Station.TWENTY_THIRD_STREET: 240,
      # Station.THIRTY_THIRD_STREET: 420
    },
    DefinedHeadsign.JOURNAL_SQUARE: {
      Station.NEWPORT: 480,
      Station.GROVE_STREET: 720,
      Station.JOURNAL_SQUARE: 960,
    },
    DefinedHeadsign.HOBOKEN: {Station.HOBOKEN: 540},
    DefinedHeadsign.JOURNAL_SQUARE_VIA_HOBOKEN: {
      Station.HOBOKEN: 780,
      Station.NEWPORT: 1020,
      Station.GROVE_STREET: 1200,
      # Station.JOURNAL_SQUARE: 1500
    },
  },
  Station.NINTH_STREET: {
    DefinedHeadsign.THIRTY_THIRD_STREET: {
      Station.FOURTEENTH_STREET: 120,
      Station.TWENTY_THIRD_STREET: 180,
      Station.THIRTY_THIRD_STREET: 360,
    },
    DefinedHeadsign.THIRTY_THIRD_VIA_HOBOKEN: {
      Station.FOURTEENTH_STREET: 120,
      Station.TWENTY_THIRD_STREET: 180,
      # Station.THIRTY_THIRD_STREET: 360
    },
    DefinedHeadsign.JOURNAL_SQUARE: {
      Station.CHRISTOPHER_STREET: 60,
      Station.NEWPORT: 540,
      Station.GROVE_STREET: 780,
      Station.JOURNAL_SQUARE: 1020,
    },
    DefinedHeadsign.HOBOKEN: {Station.CHRISTOPHER_STREET: 60, Station.HOBOKEN: 600},
    DefinedHeadsign.JOURNAL_SQUARE_VIA_HOBOKEN: {
      Station.CHRISTOPHER_STREET: 60,
      Station.HOBOKEN: 840,
      Station.NEWPORT: 1080,
      Station.GROVE_STREET: 1260,
      # Station.JOURNAL_SQUARE: 1560
    },
  },
  Station.FOURTEENTH_STREET: {
    DefinedHeadsign.THIRTY_THIRD_STREET: {
      Station.TWENTY_THIRD_STREET: 60,
      Station.THIRTY_THIRD_STREET: 240,
    },
    DefinedHeadsign.THIRTY_THIRD_VIA_HOBOKEN: {
      Station.TWENTY_THIRD_STREET: 60,
      # Station.THIRTY_THIRD_STREET: 240
    },
    DefinedHeadsign.JOURNAL_SQUARE: {
      Station.NINTH_STREET: 120,
      Station.CHRISTOPHER_STREET: 180,
      Station.NEWPORT: 660,
      Station.GROVE_STREET: 900,
      Station.JOURNAL_SQUARE: 1140,
    },
    DefinedHeadsign.HOBOKEN: {
      Station.NINTH_STREET: 120,
      Station.CHRISTOPHER_STREET: 180,
      Station.HOBOKEN: 720,
    },
    DefinedHeadsign.JOURNAL_SQUARE_VIA_HOBOKEN: {
      Station.NINTH_STREET: 120,
      Station.CHRISTOPHER_STREET: 180,
      Station.HOBOKEN: 960,
      Station.NEWPORT: 1200,
      Station.GROVE_STREET: 1380,
      # Station.JOURNAL_SQUARE: 1680
    },
  },
  Station.TWENTY_THIRD_STREET: {
    DefinedHeadsign.THIRTY_THIRD_STREET: {Station.THIRTY_THIRD_STREET: 180},
    DefinedHeadsign.THIRTY_THIRD_VIA_HOBOKEN: {
      # Station.THIRTY_THIRD_STREET: 180
    },
    DefinedHeadsign.JOURNAL_SQUARE: {
      Station.FOURTEENTH_STREET: 60,
      Station.NINTH_STREET: 180,
      Station.CHRISTOPHER_STREET: 240,
      Station.NEWPORT: 720,
      Station.GROVE_STREET: 960,
      Station.JOURNAL_SQUARE: 1200,
    },
    DefinedHeadsign.HOBOKEN: {
      Station.FOURTEENTH_STREET: 60,
      Station.NINTH_STREET: 180,
      Station.CHRISTOPHER_STREET: 240,
      Station.HOBOKEN: 780,
    },
    DefinedHeadsign.JOURNAL_SQUARE_VIA_HOBOKEN: {
      Station.FOURTEENTH_STREET: 60,
      Station.NINTH_STREET: 180,
      Station.CHRISTOPHER_STREET: 240,
      Station.HOBOKEN: 1020,
      Station.NEWPORT: 1260,
      Station.GROVE_STREET: 1440,
      # Station.JOURNAL_SQUARE: 1740
    },
  },
  Station.THIRTY_THIRD_STREET: {
    DefinedHeadsign.JOURNAL_SQUARE: {
      Station.TWENTY_THIRD_STREET: 180,
      Station.FOURTEENTH_STREET: 240,
      Station.NINTH_STREET: 360,
      Station.CHRISTOPHER_STREET: 420,
      Station.NEWPORT: 900,
      Station.GROVE_STREET: 1140,
      Station.JOURNAL_SQUARE: 1380,
    },
    DefinedHeadsign.HOBOKEN: {
      Station.TWENTY_THIRD_STREET: 180,
      Station.FOURTEENTH_STREET: 240,
      Station.NINTH_STREET: 360,
      Station.CHRISTOPHER_STREET: 420,
      Station.HOBOKEN: 960,
    },
    DefinedHeadsign.JOURNAL_SQUARE_VIA_HOBOKEN: {
      Station.TWENTY_THIRD_STREET: 120,
      Station.FOURTEENTH_STREET: 180,
      Station.NINTH_STREET: 300,
      Station.CHRISTOPHER_STREET: 360,
      Station.HOBOKEN: 1140,
      Station.NEWPORT: 1380,
      Station.GROVE_STREET: 1560,
      # Station.JOURNAL_SQUARE: 1860
    },
  },
  Station.HOBOKEN: {
    DefinedHeadsign.THIRTY_THIRD_STREET: {
      Station.CHRISTOPHER_STREET: 540,
      Station.NINTH_STREET: 600,
      Station.FOURTEENTH_STREET: 720,
      Station.TWENTY_THIRD_STREET: 780,
      Station.THIRTY_THIRD_STREET: 960,
    },
    DefinedHeadsign.THIRTY_THIRD_VIA_HOBOKEN: {
      Station.CHRISTOPHER_STREET: 540,
      Station.NINTH_STREET: 600,
      Station.FOURTEENTH_STREET: 720,
      Station.TWENTY_THIRD_STREET: 780,
      Station.THIRTY_THIRD_STREET: 960,
    },
    DefinedHeadsign.WORLD_TRADE_CENTER: {
      Station.NEWPORT: 240,
      Station.EXCHANGE_PLACE: 420,
      Station.WORLD_TRADE_CENTER: 720,
    },
    DefinedHeadsign.JOURNAL_SQUARE_VIA_HOBOKEN: {
      Station.NEWPORT: 240,
      Station.GROVE_STREET: 480,
      # Station.JOURNAL_SQUARE: 780
    },
  },
}
