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

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
