module.exports = {
    transform: {
      "^.+\\.(js|jsx)$": "babel-jest"
    },
    testEnvironment: "jsdom",
    collectCoverage: true, // Enables coverage report
    collectCoverageFrom: ["src/**/*.{js,jsx}"], // Ensure coverage includes JSX files
    coverageDirectory: "coverage",
    coverageReporters: ["text", "lcov"], // Outputs coverage in text & HTML format
  };
  