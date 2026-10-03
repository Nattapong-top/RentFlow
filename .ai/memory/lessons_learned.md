# Lessons Learned

> บันทึกบทเรียนที่ได้จากการพัฒนาโปรเจค
> เพื่อไม่ให้ทีมทำผิดซ้ำ และให้ AI เรียนรู้จากประสบการณ์ที่ผ่านมา

---

## 💡 Technical Lessons

<!-- เพิ่ม Technical Lessons ที่นี่ -->

---

## 🎯 Process Lessons

### 1. ต้องสร้าง feat/ branch ก่อนทุกครั้งที่เริ่ม feature หรือ refactor

**สถานการณ์**: จุก commit งาน refactor PricingAmount ทับลงบน branch เดิม (`refactor/non-negative-decimal-vo`) โดยไม่ได้สร้าง `feat/` branch ใหม่ตาม branch strategy ที่กำหนดใน `workproject.md`

**บทเรียน**: ทุกครั้งที่เริ่มงานใหม่ ต้องทำตาม workflow GitHub PR + Auto-Merge นี้เสมอ:
```bash
git pull origin main
git checkout -b feat/<feature-name>
# ... implement + test (make all-tests ผ่าน)
git push origin feat/<feature-name>
# สร้าง Pull Request บน GitHub
# รอ GitHub Actions ✅ pass → Auto-Merge จะ merge เองโดยอัตโนมัติ
git checkout main
git pull origin main
git branch -d feat/<feature-name>
git push origin --delete feat/<feature-name>
```

**ผลลัพธ์**: branch history สะอาด PR + GitHub Actions auto-merge ช่วยติดตามและ verify โค้ด ไม่ต้องกด merge button เอง

---

## 🤝 Collaboration Lessons

<!-- เพิ่ม Collaboration Lessons ที่นี่ -->

---

## 🔮 Future Recommendations

<!-- เพิ่ม Recommendations สำหรับอนาคตที่นี่ -->

---

## รูปแบบ Lesson Learned

```markdown
### X. ชื่อบทเรียน

**สถานการณ์**: เกิดอะไรขึ้น

**บทเรียน**: สิ่งที่เรียนรู้

**ผลลัพธ์**: ผลของการนำไปใช้
```
