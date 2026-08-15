// 注入浏览器执行的排版自检逻辑。
// 读取每个带 data-expected 的文本容器几何信息，检测掉字 / 溢出 / 越界。
// 由 screenshot.py 读取本文件内容并 page.evaluate 执行。
window.__audit = function () {
  const issues = [];
  const cv = document.querySelector('.poster-canvas');
  if (!cv) return [{ type: 'NO_CANVAS', field: '', px: 0, tag: 'BODY' }];
  const cRect = cv.getBoundingClientRect();
  const els = document.querySelectorAll('[data-expected]');
  els.forEach(function (el) {
    const r = el.getBoundingClientRect();
    const ox = el.scrollWidth - el.clientWidth;   // 横向溢出（单行 nowrap 被裁）
    const oy = el.scrollHeight - el.clientHeight;  // 纵向溢出（高度写死被裁）
    const exp = (el.getAttribute('data-expected') || '').slice(0, 24);
    const tag = el.tagName + (el.className ? '.' + el.className : '');
    if (ox > 1) issues.push({ type: '横向掉字', field: exp, px: Math.round(ox), tag: tag });
    if (oy > 1) issues.push({ type: '纵向掉字', field: exp, px: Math.round(oy), tag: tag });
    if (r.right > cRect.right + 1 || r.bottom > cRect.bottom + 1 || r.left < cRect.left - 1)
      issues.push({ type: '越界裁切', field: exp, px: 0, tag: tag });
  });
  return issues;
};

// 自动修复：返回需要修复的元素策略（缩放字号 / 放开高度）
window.__fix = function () {
  const fixed = [];
  document.querySelectorAll('[data-expected]').forEach(function (el) {
    const ox = el.scrollWidth - el.clientWidth;
    const oy = el.scrollHeight - el.clientHeight;
    if (ox > 1) {
      const cur = parseFloat(getComputedStyle(el).fontSize) || 16;
      const next = Math.max(10, cur * 0.92);
      el.style.fontSize = next + 'px';
      // 单行溢出时允许换行兜底
      if (getComputedStyle(el).whiteSpace === 'nowrap') el.style.whiteSpace = 'normal';
      fixed.push({ tag: el.tagName, action: 'font-size->' + next.toFixed(1) });
    }
    if (oy > 1) {
      el.style.height = 'auto';
      el.style.minHeight = (parseFloat(getComputedStyle(el).minHeight) || 0) + 'px';
      el.style.overflow = 'visible';
      fixed.push({ tag: el.tagName, action: 'height->auto' });
    }
  });
  return fixed;
};
