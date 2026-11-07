import { describe, expect, it } from "vitest";

import { router } from "./router";

describe("router", () => {
  it("has no login route", () => {
    const names = router.getRoutes().map((route) => route.name);
    const paths = router.getRoutes().map((route) => route.path);
    expect(names).not.toContain("login");
    expect(paths).not.toContain("/login");
  });
});
