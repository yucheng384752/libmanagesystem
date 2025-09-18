describe('首頁功能', () => {
  it('應該可以載入首頁', () => {
    cy.visit('http://localhost:3000');
    cy.contains('圖書館測試系統');
  });

  it('應該可以點擊登入/註冊', () => {
    cy.visit('http://localhost:3000');
    cy.contains('登入 / 註冊').click();
    cy.url().should('include', '/login');
  });
});