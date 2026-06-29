export const mockData = {
  synthetic: {
    meta: {
      elephant_detected: "5/5",
      mice_avg_error_classic: 340,
      mice_avg_error_mixed: 12,
    },
    top10: [
      {
        ip: "10.0.0.1",
        true_count: 5000,
        estimate_classic: 17000,
        estimate_mixed: 5200,
      },
      {
        ip: "10.0.0.2",
        true_count: 4800,
        estimate_classic: 16000,
        estimate_mixed: 4900,
      },
    ],
  },
  real: {
    meta: {
      elephant_detected: "85/100",
      mice_avg_error_classic: 45,
      mice_avg_error_mixed: 8,
    },
    top10: [
      {
        ip: "192.168.1.1",
        true_count: 120000,
        estimate_classic: 125000,
        estimate_mixed: 121000,
      },
    ],
  },
};
