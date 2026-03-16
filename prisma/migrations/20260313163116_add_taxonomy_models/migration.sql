-- AlterTable
ALTER TABLE "public"."auctions" ADD COLUMN     "serviceCategoryId" INTEGER;

-- CreateTable
CREATE TABLE "public"."sectors" (
    "id" SERIAL NOT NULL,
    "name" TEXT NOT NULL,
    "slug" TEXT NOT NULL,
    "description" TEXT,
    "isActive" BOOLEAN NOT NULL DEFAULT true,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "sectors_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."studio_sectors" (
    "studioId" INTEGER NOT NULL,
    "sectorId" INTEGER NOT NULL,
    "assignedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "studio_sectors_pkey" PRIMARY KEY ("studioId","sectorId")
);

-- CreateTable
CREATE TABLE "public"."service_categories" (
    "id" SERIAL NOT NULL,
    "name" TEXT NOT NULL,
    "slug" TEXT NOT NULL,
    "description" TEXT,
    "isActive" BOOLEAN NOT NULL DEFAULT true,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    "sectorId" INTEGER,

    CONSTRAINT "service_categories_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "sectors_slug_key" ON "public"."sectors"("slug");

-- CreateIndex
CREATE INDEX "sectors_isActive_idx" ON "public"."sectors"("isActive");

-- CreateIndex
CREATE INDEX "studio_sectors_sectorId_idx" ON "public"."studio_sectors"("sectorId");

-- CreateIndex
CREATE UNIQUE INDEX "service_categories_slug_key" ON "public"."service_categories"("slug");

-- CreateIndex
CREATE INDEX "service_categories_sectorId_isActive_idx" ON "public"."service_categories"("sectorId", "isActive");

-- CreateIndex
CREATE INDEX "auctions_serviceCategoryId_idx" ON "public"."auctions"("serviceCategoryId");

-- AddForeignKey
ALTER TABLE "public"."studio_sectors" ADD CONSTRAINT "studio_sectors_studioId_fkey" FOREIGN KEY ("studioId") REFERENCES "public"."studios"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."studio_sectors" ADD CONSTRAINT "studio_sectors_sectorId_fkey" FOREIGN KEY ("sectorId") REFERENCES "public"."sectors"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."service_categories" ADD CONSTRAINT "service_categories_sectorId_fkey" FOREIGN KEY ("sectorId") REFERENCES "public"."sectors"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."auctions" ADD CONSTRAINT "auctions_serviceCategoryId_fkey" FOREIGN KEY ("serviceCategoryId") REFERENCES "public"."service_categories"("id") ON DELETE SET NULL ON UPDATE CASCADE;
