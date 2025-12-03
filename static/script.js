
// Dropdown menu logic for avatar
const avatarMini = document.querySelector('.dashboard-avatar-mini');
const dropdownMenu = document.querySelector('.dropdown-menu');

if (avatarMini && dropdownMenu) {
  avatarMini.addEventListener('click', (e) => {
    e.stopPropagation();
    dropdownMenu.style.opacity = dropdownMenu.style.opacity === '1' ? '0' : '1';
    dropdownMenu.style.visibility = dropdownMenu.style.visibility === 'visible' ? 'hidden' : 'visible';
    dropdownMenu.style.transform = dropdownMenu.style.opacity === '1' ? 'translateY(0)' : 'translateY(-10px)';
  });
  document.addEventListener('click', (e) => {
    if (!dropdownMenu.contains(e.target) && e.target !== avatarMini) {
      dropdownMenu.style.opacity = '0';
      dropdownMenu.style.visibility = 'hidden';
      dropdownMenu.style.transform = 'translateY(-10px)';
    }
  });
}

// Blog filter functionality
document.addEventListener('DOMContentLoaded', function() {
  const filterButtons = document.querySelectorAll('.filter-btn');
  const blogCards = document.querySelectorAll('.blog-card');
  const blogGrid = document.querySelector('.blog-card-grid');

  // Sort blog posts by date on page load
  if (blogGrid && blogCards.length > 0) {
    const sortedCards = Array.from(blogCards).sort((a, b) => {
      const dateA = new Date(a.querySelector('.blog-date').textContent);
      const dateB = new Date(b.querySelector('.blog-date').textContent);
      return dateB - dateA; // Newest first
    });
    
    // Re-append cards in sorted order
    sortedCards.forEach(card => blogGrid.appendChild(card));
  }

  if (filterButtons.length > 0 && blogCards.length > 0) {
    filterButtons.forEach(button => {
      button.addEventListener('click', function() {
        const filter = this.getAttribute('data-filter');
        
        // Update active button
        filterButtons.forEach(btn => btn.classList.remove('active'));
        this.classList.add('active');
        
        // Filter blog cards
        blogCards.forEach(card => {
          const tags = card.getAttribute('data-tags');
          
          if (filter === 'all' || (tags && tags.includes(filter))) {
            card.style.display = 'block';
            card.style.animation = 'fadeSlideUp 0.6s ease forwards';
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            
            // Stagger the animation
            setTimeout(() => {
              card.style.opacity = '1';
              card.style.transform = 'translateY(0)';
            }, 100);
          } else {
            card.style.display = 'none';
          }
        });
      });
    });
  }

});