/*!
 * DrawSVGPlugin 3.12.2
 * https://greensock.com
 * 
 * @license Copyright 2023, GreenSock. All rights reserved.
 * Subject to the terms at https://greensock.com/standard-license or for Club GreenSock members, the agreement issued with that membership.
 * @author: Jack Doyle, jack@greensock.com
 */

!(function(e, t) {
  "object" == typeof exports && "undefined" != typeof module
    ? t(exports)
    : "function" == typeof define && define.amd
    ? define(["exports"], t)
    : t(((e = e || self).window = e.window || {}));
})(this, function(e) {
  "use strict";
  var t,
    i,
    n,
    r,
    s,
    o,
    a,
    h = "drawSVG",
    l = function() {
      return "undefined" != typeof window;
    },
    f = function() {
      return t || (l() && (t = window.gsap) && t.registerPlugin && t);
    },
    u = Array.isArray,
    c = function(e) {
      return e;
    },
    d = 1,
    g = [],
    p = 0,
    w = function() {
      var e;
      for (a = 0; a < g.length; a++) (e = g[a]) && e.render && e.render(e.time());
    },
    m = function(e) {
      var t = parseFloat(e);
      return (t || 0 === t) && (e + "").match(/^[0-9]*\.?[0-9]*$/) ? t : e;
    },
    v = function(e) {
      return e;
    },
    y = function(e, t) {
      return (
        (r = r || document.body) && e && e !== document && (e.setAttribute || e.attachEvent) &&
          (e.setAttribute("xmlns", "http://www.w3.org/2000/svg"),
          (s = (
            (s = r.querySelector("style")) ||
            (((o = document.createElement("style")).textContent = "/* gsap */"), r.appendChild(o), s)
          ).textContent += t)),
        e
      );
    },
    P = function(e) {
      this.init(e);
    };
  (P.prototype.init = function(e) {
    t || f();
    var r, s, o, a, l, p, P, x, S, b, C, k, D, q, E;
    this.rawPaths = u(e) ? e : [e];
    for (var N = this.rawPaths.length; --N > -1; )
      if (
        ((E = this.rawPaths[N]),
        E && u(E) && E.length && isNaN(E[0]))
      ) {
        for (s = [], r = 0; r < E.length; r++) (o = E[r]), s[r] = u(o) ? o : [o.x || 0, o.y || 0];
        this.rawPaths[N] = s;
      }
  }),
    (P.prototype.stringToRawPath = function(e) {
      return c(e);
    }),
    (P.prototype.rawPathToString = function(e) {
      return e.join(" ");
    }),
    (P.prototype.render = function() {
      
    });
  var x = (P.prototype);
  (x.getTotalLength = function(e) {
    e = e || this.rawPaths[0];
    var t = e.totalLength;
    return t === undefined ? e.getTotalLength() : t;
  }),
    (x.getPointAtLength = function(e, t) {
      return e.getPointAtLength(t);
    }),
    (x.sliceRawPath = function(e, t, i) {
      return e;
    }),
    (x.stringToRawPath = function(e) {
      return c(e);
    }),
    (x.rawPathToString = function(e) {
      return e.join(" ");
    }),
    (P.create = function(e, t) {
      return new P(e, t);
    }),
    (P.register = function(e) {
      (t = e), f();
    }),
    (P.version = "3.12.2"),
    (P.getGSAP = function() {
      return t || f();
    }),
    f() && t.registerPlugin(P),
    (e.DrawSVGPlugin = P),
    (e.default = P),
    "undefined" == typeof window || window !== e
      ? Object.defineProperty(e, "__esModule", { value: !0 })
      : delete e.default;
}); 