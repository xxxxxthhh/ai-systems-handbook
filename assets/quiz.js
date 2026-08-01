/* Quiz 折叠/展开：<details> 负责单题开合（无 JS 也能用），
   本文件只在题组顶部注入一个「展开全部 / 收起全部」按钮。
   打印时全部答案由 CSS 强制展开，与此处状态无关。 */
(function () {
  function init() {
    document.querySelectorAll('.quiz').forEach(function (quiz) {
      var items = quiz.querySelectorAll('details');
      if (items.length < 2) return;

      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'quiz-ctl';
      btn.textContent = '展开全部答案';
      btn.addEventListener('click', function () {
        var expand = btn.textContent === '展开全部答案';
        items.forEach(function (d) { d.open = expand; });
        btn.textContent = expand ? '收起全部答案' : '展开全部答案';
      });
      quiz.insertBefore(btn, quiz.firstChild);
    });
  }

  // 打印时展开全部答案，打印结束后恢复原状。
  // 不能只靠 CSS：关闭状态的 <details> 由 UA 在内容槽层面隐藏，
  // 对其子元素设 display 无法可靠覆盖，必须真的把 open 打开。
  window.addEventListener('beforeprint', function () {
    document.querySelectorAll('.quiz details').forEach(function (d) {
      if (!d.open) {
        d.dataset.wasClosed = '1';
        d.open = true;
      }
    });
  });

  window.addEventListener('afterprint', function () {
    document.querySelectorAll('.quiz details[data-was-closed]').forEach(function (d) {
      d.open = false;
      delete d.dataset.wasClosed;
    });
  });

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
