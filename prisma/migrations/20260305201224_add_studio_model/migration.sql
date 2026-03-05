-- AlterTable
ALTER TABLE "public"."auctions" ADD COLUMN     "studioId" INTEGER;

-- AlterTable
ALTER TABLE "public"."users" ADD COLUMN     "studioId" INTEGER;

-- CreateTable
CREATE TABLE "public"."studios" (
    "id" SERIAL NOT NULL,
    "name" TEXT NOT NULL,
    "logoUrl" TEXT,
    "googleMapsUrl" TEXT,
    "address" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "studios_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "auctions_studioId_idx" ON "public"."auctions"("studioId");

-- AddForeignKey
ALTER TABLE "public"."users" ADD CONSTRAINT "users_studioId_fkey" FOREIGN KEY ("studioId") REFERENCES "public"."studios"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."auctions" ADD CONSTRAINT "auctions_studioId_fkey" FOREIGN KEY ("studioId") REFERENCES "public"."studios"("id") ON DELETE SET NULL ON UPDATE CASCADE;
